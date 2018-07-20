/*
 * Copyright (c) 2013 Juniper Networks, Inc. All rights reserved.
 */

#ifndef vnsw_tungsten_agent_init_hpp
#define vnsw_tungsten_agent_init_hpp

#include <boost/program_options.hpp>
#include <init/tungsten_init_common.h>
#include <tungsten/pkt0_interface.h>

class Agent;
class AgentParam;
class DiagTable;
class ServicesModule;
class PktModule;

// The class to drive agent initialization.
// Defines control parameters used to enable/disable agent features
class TungstenAgentInit : public TungstenInitCommon {
public:
    TungstenAgentInit();
    virtual ~TungstenAgentInit();

    void ProcessOptions(const std::string &config_file,
                        const std::string &program_name);

    // Initialization virtual methods
    void FactoryInit();
    void CreateModules();
    void InitDone();

    // Shutdown virtual methods
    void ModulesShutdown();
    void KSyncShutdown();
    void UveShutdown();
    void StatsCollectorShutdown();
    void FlowStatsCollectorShutdown();
    void WaitForIdle();

private:
    std::auto_ptr<KSync> ksync_;
    std::auto_ptr<AgentUveBase> uve_;
    std::auto_ptr<VrouterControlInterface> pkt0_;
    std::auto_ptr<AgentStatsCollector> stats_collector_;
    std::auto_ptr<FlowStatsManager> flow_stats_manager_;
    std::auto_ptr<PortIpcHandler> port_ipc_handler_;
    std::auto_ptr<RESTServer> rest_server_;

    DISALLOW_COPY_AND_ASSIGN(TungstenAgentInit);
};

#endif // vnsw_tungsten_agent_init_hpp
