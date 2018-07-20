#!/usr/bin/env bash
set -x
function issu_tungsten_set_supervisord_config_files {
    local cmd="openstack-config --set /etc/tungsten/supervisord_config_files/$1.ini program:$1"
    $cmd autostart $2
    $cmd autorestart $2
    $cmd killasgroup $2
}

function issu_tungsten_prepare_new_control_node {
    tungsten-status
    val="$(lsb_release -sr | cut -d \. -f 1)"
    if [ $val == 14 ]
    then
        issu_tungsten_set_supervisord_config_files 'tungsten-device-manager' 'false'
        issu_tungsten_set_supervisord_config_files 'tungsten-svc-monitor' 'false'
        issu_tungsten_set_supervisord_config_files 'tungsten-schema' 'false'

        openstack-config --set /etc/tungsten/supervisord_config_files/tungsten-config-nodemgr.ini eventlistener:tungsten-config-nodemgr autorestart false
        openstack-config --set /etc/tungsten/supervisord_config_files/tungsten-config-nodemgr.ini eventlistener:tungsten-config-nodemgr autostart false

        service tungsten-config-nodemgr stop
        service tungsten-control stop
        service tungsten-schema stop
        service tungsten-svc-monitor stop
        service tungsten-device-manager stop
    fi
    if [ $val == 16 ]
    then
        systemctl stop tungsten-config-nodemgr
        systemctl stop tungsten-control
        systemctl stop tungsten-schema
        systemctl stop tungsten-svc-monitor
        systemctl stop tungsten-device-manager
        systemctl disable tungsten-config-nodemgr
        systemctl disable tungsten-svc-monitor
	systemctl disable tungsten-device-manager
	systemctl disable tungsten-schema
    fi
    tungsten-status
}

function issu_tungsten_post_new_control_node {
    tungsten-status
    val="$(lsb_release -sr | cut -d \. -f 1)"
    if [ $val == 14 ]
    then
            #openstack-config --set /etc/tungsten/supervisord_config.conf include files \"/etc/tungsten/supervisord_config_files/*.ini\"
            
    issu_tungsten_set_supervisord_config_files 'tungsten-device-manager' 'true'
    issu_tungsten_set_supervisord_config_files 'tungsten-svc-monitor' 'true'
    issu_tungsten_set_supervisord_config_files 'tungsten-schema' 'true'

    openstack-config --del /etc/tungsten/supervisord_config_files/tungsten-config-nodemgr.ini eventlistener:tungsten-config-nodemgr autorestart
    openstack-config --del /etc/tungsten/supervisord_config_files/tungsten-config-nodemgr.ini eventlistener:tungsten-config-nodemgr autostart
    service tungsten-config-nodemgr start
    service tungsten-control start
    service tungsten-schema start
    service tungsten-svc-monitor start
    service tungsten-device-manager start
    fi
    if [ $val == 16 ]
    then
        systemctl enable tungsten-config-nodemgr
        systemctl enable tungsten-svc-monitor
        systemctl enable tungsten-device-manager
	systemctl enable tungsten-schema
        systemctl start tungsten-config-nodemgr
        systemctl start tungsten-control
        systemctl start tungsten-schema
        systemctl start tungsten-svc-monitor
        systemctl start tungsten-device-manager
    fi
    tungsten-status

}

function issu_pre_sync {
    tungsten-issu-pre-sync -c /etc/tungsten/tungsten-issu.conf
}

function issu_run_sync {
    val="$(lsb_release -sr | cut -d \. -f 1)"
    if [ $val == 14 ]
    then
        supervisorctl restart supervisord_issu
    fi
    if [ $val == 16 ]
    then
        systemctl enable tungsten-issu-run-sync
        systemctl restart tungsten-issu-run-sync
    fi
}

function issu_post_sync {
    val="$(lsb_release -sr | cut -d \. -f 1)"
    if [ $val == 14 ]
    then
        supervisorctl stop supervisord_issu
    fi
    if [ $val == 16 ]
    then
        systemctl stop tungsten-issu-run-sync
        systemctl disable tungsten-issu-run-sync
    fi
    tungsten-issu-post-sync -c /etc/tungsten/tungsten-issu.conf
    tungsten-issu-zk-sync -c /etc/tungsten/tungsten-issu.conf
}

function issu_tungsten_generate_conf {
    local myfile="/tmp/tungsten-issu.conf"
    issu_tungsten_get_and_set_old_conf $1 $myfile
    issu_tungsten_get_and_set_new_conf $2 $myfile
    echo $1 $2
}

function issu_tungsten_get_and_set_old_conf {
    local get_old_cmd="openstack-config --get  $1  DEFAULTS"
    local has_old_cmd="openstack-config --has $1 DEFAULTS"
    local set_cmd="openstack-config --set $2 DEFAULTS"

    cmd="$get_old_cmd cassandra_server_list"
    val=$($cmd)
    $set_cmd   old_cassandra_address_list "$val"

    cmd="$get_old_cmd zk_server_ip"
    val=$($cmd)
    $set_cmd old_zookeeper_address_list "$val"

    cmd="$has_old_cmd rabbit_user"
    val=$($cmd)
    if [ $val == 1 ]
    then
        cmd="$get_old_cmd rabbit_user"
        val=$($cmd)
        $set_cmd old_rabbit_user "$val"
    fi
   
    cmd="$has_old_cmd rabbit_password"
    val=$($cmd)
    if [ $val == 1 ]
    then
        cmd="$get_old_cmd rabbit_password"
        val=$($cmd)
        $set_cmd old_rabbit_password "$val"
    fi

    cmd="$has_old_cmd rabbit_vhost"
    val=$($cmd)
    if [ $val == 1 ]
    then
        cmd="$get_old_cmd rabbit_vhost"
        val=$($cmd)
        $set_cmd old_rabbit_vhost "$val"
    fi
 
    cmd="$has_old_cmd rabbit_ha_mode"
    val=$($cmd)
    if [ $val == 1 ]
    then
        cmd="$get_old_cmd rabbit_ha_mode"
        val=$($cmd)
        $set_cmd old_rabbit_ha_mode "$val"
    fi

    cmd="$has_old_cmd rabbit_port"
    val=$($cmd)
    if [ $val == 1 ]
    then
        cmd="$get_old_cmd rabbit_port"
        val=$($cmd)
        $set_cmd old_rabbit_port "$val"
    fi

    cmd="$has_old_cmd rabbit_server"
    val=$($cmd)
    if [ $val == 1 ]
    then
        cmd="$get_old_cmd rabbit_server"
        val=$($cmd)
        $set_cmd old_rabbit_address_list "$val"
    fi

    cmd="$has_old_cmd cluster_id"
    val=$($cmd)
    if [ $val == 1 ]
    then
        cmd="$get_old_cmd cluster_id"
        val=$($cmd)
        $set_cmd odb_prefix "$val"
    fi


}

function issu_tungsten_get_and_set_new_conf {
    local get_new_cmd="openstack-config --get $1 DEFAULTS"
    local set_cmd="openstack-config --set $2 DEFAULTS"
    local has_new_cmd="openstack-config --has $1 DEFAULTS"

    cmd="$get_new_cmd cassandra_server_list"
    val=$($cmd)
    $set_cmd new_cassandra_address_list "$val"

    cmd="$get_new_cmd zk_server_ip"
    val=$($cmd)
    $set_cmd new_zookeeper_address_list "$val"

    cmd="$has_new_cmd rabbit_user"
    val=$($cmd)
    if [ $val == 1 ]
    then
        cmd="$get_new_cmd rabbit_user"
        val=$($cmd)
        $set_cmd new_rabbit_user "$val"
    fi
   
    cmd="$has_new_cmd rabbit_password"
    val=$($cmd)
    if [ $val == 1 ]
    then
        cmd="$get_new_cmd rabbit_password"
        val=$($cmd)
        $set_cmd new_rabbit_password "$val"
    fi

    cmd="$has_new_cmd rabbit_vhost"
    val=$($cmd)
    if [ $val == 1 ]
    then
        cmd="$get_new_cmd rabbit_vhost"
        val=$($cmd)
        $set_cmd new_rabbit_vhost "$val"
    fi
 
    cmd="$has_new_cmd rabbit_ha_mode"
    val=$($cmd)
    if [ $val == 1 ]
    then
        cmd="$get_new_cmd rabbit_ha_mode"
        val=$($cmd)
        $set_cmd new_rabbit_ha_mode "$val"
    fi

    cmd="$has_new_cmd rabbit_port"
    val=$($cmd)
    if [ $val == 1 ]
    then
        cmd="$get_new_cmd rabbit_port"
        val=$($cmd)
        $set_cmd new_rabbit_port "$val"
    fi

    cmd="$has_new_cmd rabbit_server"
    val=$($cmd)
    if [ $val == 1 ]
    then
        cmd="$get_new_cmd rabbit_server"
        val=$($cmd)
        $set_cmd new_rabbit_address_list "$val"
    fi

    cmd="$has_new_cmd cluster_id"
    val=$($cmd)
    if [ $val == 1 ]
    then
        cmd="$get_new_cmd cluster_id"
        val=$($cmd)
        $set_cmd ndb_prefix "$val"
    fi
}

function issu_tungsten_peer_control_nodes {
    python /opt/tungsten/utils/provision_pre_issu.py --conf /etc/tungsten/tungsten-issu.conf
}

function issu_tungsten_finalize_config {
    python /opt/tungsten/utils/provision_issu.py --conf /etc/tungsten/tungsten-issu.conf
}

function issu_tungsten_fetch_api_conf {
    cp /etc/tungsten/tungsten-api.conf /etc/tungstenctl/tungsten-api.conf
}

function issu_tungsten_set_conf {
    cp /etc/tungstenctl/tungsten-issu.conf /etc/tungsten/tungsten-issu.conf
}

function myfunc {
    echo "Hello World $1"
}

ARGC=$#
if [ $ARGC == 0 ]
then
    echo "Usage: $0 <function name> <arguments>"
    exit;
fi

case $1 in
    myfunc)
      if [ $ARGC == 2 ]
      then
        $1 $2
        exit
      fi
      echo "Usage: $0 $1 <arguments>"
      ;;
    issu_tungsten_generate_conf)
      if [ $ARGC == 2 ]
      then
        $1 $2 $3
        exit
      fi
      echo "Usage: $0 $1 <arguments>"
      ;;
    issu_tungsten_prepare_new_control_node)
      if [ $ARGC == 1 ]
      then
        $1
        exit
      fi
      echo "Usage: $0 $1 "
      ;;
    issu_tungsten_post_new_control_node)
      if [ $ARGC == 1 ]
      then
        $1
        exit
      fi
      echo "Usage: $0 $1 "
      ;;
    issu_pre_sync)
      if [ $ARGC == 1 ]
      then
        $1
        exit
      fi
      echo "Usage: $0 $1 "
      ;;
    issu_run_sync)
      if [ $ARGC == 1 ]
      then
        $1
        exit
      fi
      echo "Usage: $0 $1 "
      ;;
    issu_post_sync)
      if [ $ARGC == 1 ]
      then
        $1
        exit
      fi
      echo "Usage: $0 $1 "
      ;;
    issu_tungsten_finalize_config)
      if [ $ARGC == 1 ]
      then
        $1
        exit
      fi
      echo "Usage: $0 $1 "
      ;;
    issu_tungsten_fetch_api_conf)
      if [ $ARGC == 1 ]
      then
        $1
        exit
      fi
      echo "Usage: $0 $1 "
      ;;
    issu_tungsten_set_conf)
      if [ $ARGC == 1 ]
      then
        $1
        exit
      fi
      echo "Usage: $0 $1 "
      ;;
    issu_tungsten_peer_control_nodes)
      if [ $ARGC == 1 ]
      then
        $1
        exit
      fi
      echo "Usage: $0 $1 "
      ;;

    *)
      echo -e "Unrecognized function $1"
      ;;
esac
