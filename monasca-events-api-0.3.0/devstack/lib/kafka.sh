#!/bin/bash

# Copyright 2017 FUJITSU LIMITED
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


_XTRACE_KAFKA=$(set +o | grep xtrace)
set +o xtrace

function is_kafka_enabled {
    is_service_enabled monasca-kafka && return 0
    return 1
}

function create_kafka_topic {
    if is_kafka_enabled; then
        /opt/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 4 --topic $1
    fi
}

$_XTRACE_KAFKA
