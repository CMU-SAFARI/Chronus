#include "dram_controller/bhcontroller.h"
#include "memory_system/memory_system.h"
#include "frontend/frontend.h"
#include "frontend/impl/processor/bhO3/bhllc.h"
#include "frontend/impl/processor/bhO3/bhO3.h"

namespace Ramulator {

class ConstantLatencyDRAMController final : public IBHDRAMController, public Implementation {
RAMULATOR_REGISTER_IMPLEMENTATION(IBHDRAMController, ConstantLatencyDRAMController, "ConstantLatencyDRAMController", "Constant Latency DRAM controller.");

private:
	std::deque<Request> pending;          // A queue for read requests that are about to finish (callback after RL)

	ReqBuffer m_active_buffer;          
	ReqBuffer m_priority_buffer;          

	int m_bank_addr_idx = -1;
	uint64_t m_latency_clk = 0;
	uint64_t m_serve_clk = 0;

	uint64_t m_latency_ns = 0;

public:
	void init() override {
		m_latency_ns = param<uint64_t>("latency_ns").default_val(0);

		m_scheduler = create_child_ifce<IBHScheduler>();
		m_refresh = create_child_ifce<IRefreshManager>();
		m_rowpolicy = create_child_ifce<IRowPolicy>();
	}

	void setup(IFrontEnd* frontend, IMemorySystem* memory_system) override {
		m_dram = memory_system->get_ifce<IDRAM>();
		m_bank_addr_idx = m_dram->m_levels("bank");

		m_priority_buffer.max_size = INT_MAX;

		m_latency_clk = m_latency_ns / ((float) m_dram->m_timing_vals("tCK_ps") / 1000.0f);
	}

	bool send(Request& req) override {
		if (req.type_id == Request::Type::Read) {
			m_serve_clk = std::max<uint64_t>(m_clk, m_serve_clk) + m_latency_clk;
			req.depart = m_serve_clk;
			pending.push_back(req);
		}
		return true;
	}

	bool priority_send(Request& req) override {
		req.final_command = m_dram->m_request_translations(req.type_id);
		bool is_success = false;
		is_success = m_priority_buffer.enqueue(req);
		return is_success;
	}

	void tick() override {
		m_clk++;
		// 1. Serve completed reads
		serve_completed_reads();

		m_refresh->tick();
		m_scheduler->tick();

		// 2. Try to find a request to serve.
		ReqBuffer::iterator req_it;
		ReqBuffer* buffer = nullptr;
		bool request_found = schedule_request(req_it, buffer);

		// 2.1 RowPolicy
		m_rowpolicy->update(request_found, req_it);

		// 3. Update all plugins
		for (auto plugin : m_plugins) {
			plugin->update(request_found, req_it);
		}

		// 4. Finally, issue the commands to serve the request
		if (request_found) {
			// If we find a real request to serve
			m_dram->issue_command(req_it->command, req_it->addr_vec);

			// If we are issuing the last command, set depart clock cycle and move the request to the pending queue
			if (req_it->command == req_it->final_command) {
				if (req_it->type_id == Request::Type::Read) {
					req_it->depart = m_clk + m_dram->m_read_latency;
					pending.push_back(*req_it);
				} else if (req_it->type_id == Request::Type::Write) {
					// TODO: Add code to update statistics
				}
				buffer->remove(req_it);
			} else {
				if (m_dram->m_command_meta(req_it->command).is_opening) {
					m_active_buffer.enqueue(*req_it);
					buffer->remove(req_it);
				}
			}
		}
	}

private:
	/**
	 * @brief    Helper function to serve the completed read requests
	 * @details
	 * This function is called at the beginning of the tick() function.
	 * It checks the pending queue to see if the top request has received data from DRAM.
	 * If so, it finishes this request by calling its callback and poping it from the pending queue.
	 */
	void serve_completed_reads() {
		if (pending.size()) {
			// Check the first pending request
			auto& req = pending[0];
			if (req.depart <= m_clk) {
				// Request received data from dram
				if (req.depart - req.arrive > 1) {
					// Check if this requests accesses the DRAM or is being forwarded.
					// TODO add the stats back
				}

				if (req.callback) {
					// If the request comes from outside (e.g., processor), call its callback
					req.callback(req);
				}
				// Finally, remove this request from the pending queue
				pending.pop_front();
			}
		}
	}

	/**
	 * @brief    Checks if we need to switch to write mode
	 * 
	 */
	void set_write_mode() { }

	/**
	 * @brief    Helper function to find a request to schedule from the buffers.
	 * 
	 */
	bool schedule_request(ReqBuffer::iterator& req_it, ReqBuffer*& req_buffer) {
		bool request_found = false;
		// 2.1    First, check the act buffer to serve requests that are already activating (avoid useless ACTs)
		if (req_it = m_scheduler->get_best_request(m_active_buffer); req_it != m_active_buffer.end()) { 
			if (m_dram->check_ready(req_it->command, req_it->addr_vec)) {
				request_found = true;
				req_buffer = &m_active_buffer;
			}
		}
		// 2.2    If no requests can be scheduled from the act buffer, check the rest of the buffers
		if (!request_found) {
			// 2.2.1    We first check the priority buffer to prioritize e.g., maintenance requests
			if (m_priority_buffer.size() != 0) {
				req_buffer = &m_priority_buffer;
				req_it = m_priority_buffer.begin();
				req_it->command = m_dram->get_preq_command(req_it->final_command, req_it->addr_vec);
				
				request_found = m_dram->check_ready(req_it->command, req_it->addr_vec);
				if (!request_found & m_priority_buffer.size() != 0) {
					return false;
				}
			}
		}

		if (request_found) {
			if (m_dram->m_command_meta(req_it->command).is_closing) {
				auto& rowgroup = req_it->addr_vec;
				for (auto _it = m_active_buffer.begin(); _it != m_active_buffer.end(); _it++) {
					auto& _it_rowgroup = _it->addr_vec;
					bool is_matching = true;
					for (int i = 0; i < m_bank_addr_idx + 1 ; i++) {
						if (_it_rowgroup[i] != rowgroup[i] && _it_rowgroup[i] != -1 && rowgroup[i] != -1) {
							is_matching = false;
							break;
						}
					}
					if (is_matching) {
						request_found = false;
						break;
					}
				}
			}
		}
		return request_found;
	}

	void finalize() override { }
};

}   // namespace Ramulator