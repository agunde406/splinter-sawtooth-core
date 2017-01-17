# Copyright 2016 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------
import logging
from sawtooth_validator.protobuf import state_context_pb2
from sawtooth_validator.protobuf import validator_pb2
from sawtooth_validator.protobuf.validator_pb2 import Message

LOGGER = logging.getLogger(__name__)


class GetHandler(object):

    def __init__(self, context_manager):
        self._context_manager = context_manager

    def handle(self, message, responder):
        get_request = state_context_pb2.TpStateGetRequest()
        get_request.ParseFromString(message.content)
        return_values = self._context_manager.get(get_request.context_id,
                                                  get_request.addresses)
        return_list = return_values if return_values is not None else []
        LOGGER.info("GET: %s", return_list)
        entry_list = [state_context_pb2.Entry(address=a,
                                              data=d) for a, d in return_list]
        responder.send(message=validator_pb2.Message(
            sender=message.sender,
            correlation_id=message.correlation_id,
            message_type=Message.TP_STATE_GET_RESPONSE,
            content=state_context_pb2.TpStateGetResponse(
                entries=entry_list).SerializeToString()
        ))


class SetHandler(object):
    def __init__(self, context_manager):
        """

        Args:
            context_manager (sawtooth_validator.context_manager.
            ContextManager):
        """
        self._context_manager = context_manager

    def handle(self, message, responder):
        set_request = state_context_pb2.TpStateSetRequest()
        set_request.ParseFromString(message.content)
        set_values_list = [{e.address: e.data} for e in set_request.entries]
        return_value = self._context_manager.set(set_request.context_id,
                                                 set_values_list)
        response = state_context_pb2.TpStateSetResponse()
        if return_value is True:
            address_list = [e.address for e in set_request.entries]
            response.addresses.extend(address_list)
            responder.send(message=validator_pb2.Message(
                sender=message.sender,
                correlation_id=message.correlation_id,
                message_type=Message.TP_STATE_SET_RESPONSE,
                content=response.SerializeToString()
            ))
        else:
            response.addresses.extend([])
            responder.send(message=validator_pb2.Message(
                sender=message.sender,
                correlation_id=message.correlation_id,
                message_type=Message.TP_STATE_SET_RESPONSE,
                content=response.SerializeToString()
            ))
