# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from libcloud.common.base import ConnectionKey
from libcloud.common.types import LibcloudError

__all__ = [
        "LBMember",
        "LB",
        "LBDriver",
        "LBAlgorithm"
        ]

class LBMember(object):

    def __init__(self, id, ip, port):
        self.id = str(id) if id else None
        self.ip = ip
        self.port = port

    def __repr__(self):
        return ('<LBMember: id=%s, address=%s:%s>' % (self.id,
            self.ip, self.port))

class LBAlgorithm(object):
    RANDOM = 0
    ROUND_ROBIN = 1
    LEAST_CONNECTIONS = 2

DEFAULT_ALGORITHM = LBAlgorithm.ROUND_ROBIN

class LB(object):
    """
    Provide a common interface for handling Load Balancers.
    """

    def __init__(self, id, name, state, ip, port, driver):
        self.id = str(id) if id else None
        self.name = name
        self.state = state
        self.ip = ip
        self.port = port
        self.driver = driver

    def attach_compute_node(self, node):
        return self.driver.balancer_attach_compute_node(node)

    def detach_member(self, member):
        return self.driver.balancer_detach_member(self, member)

    def list_members(self):
        return self.driver.balancer_list_members(self)

    def __repr__(self):
        return ('<LB: id=%s, name=%s, state=%s>' % (self.id,
                self.name, self.state))


class LBDriver(object):
    """
    A base LBDriver class to derive from

    This class is always subclassed by a specific driver.

    """

    connectionCls = ConnectionKey
    _ALGORITHM_TO_VALUE_MAP = {}
    _VALUE_TO_ALGORITHM_MAP = {}

    def __init__(self, key, secret=None, secure=True):
        self.key = key
        self.secret = secret
        args = [self.key]

        if self.secret is not None:
            args.append(self.secret)

        args.append(secure)

        self.connection = self.connectionCls(*args)
        self.connection.driver = self
        self.connection.connect()

    def list_balancers(self):
        """
        List all loadbalancers

        @return: C{list} of L{LB} objects

        """

        raise NotImplementedError, \
                'list_balancers not implemented for this driver'

    def create_balancer(self, **kwargs):
        """
        Create a new load balancer instance

        @keyword name: Name of the new load balancer (required)
        @type name: C{str}
        @keyword port: Port the load balancer should listen on (required)
        @type port: C{str}
        @keyword algorithm: Load balancing algorithm (defaults to round robin)
        @type algorithm: C{LBAlgorithm}
        @keyword members: C{list} of L{LBNode}s to attach to balancer
        @type: C{list} of L{LBNode}s

        """

        raise NotImplementedError, \
                'create_balancer not implemented for this driver'

    def destroy_balancer(self, balancer):
        """Destroy a load balancer

        @return: C{bool} True if the destroy was successful, otherwise False

        """

        raise NotImplementedError, \
                'destroy_balancer not implemented for this driver'

    def balancer_detail(self, **kwargs):
        """
        Returns a detailed info about load balancer given by
        existing L{LB} object or its id

        @keyword balancer: L{LB} object you already fetched using list method for example
        @type balancer: L{LB}
        @keyword balancer_id: id of a load balancer you want to fetch
        @type balancer_id: C{str}

        @return: L{LB}

        """

        raise NotImplementedError, \
                'balancer_detail not implemented for this driver'

    def balancer_attach_compute_node(self, balancer, node):
      """
      Attach a compute node as a member to the load balancer.

      @keyword node: Member to join to the balancer
      @type member: C{libcloud.compute.base.Node}
      @return {LBMember} Member after joining the balancer.
      """

      return self.attach_member(LBMember(None, node.public_ip[0], balancer.port))

    def balancer_attach_member(self, balancer, member):
        """
        Attach a member to balancer

        @keyword member: Member to join to the balancer
        @type member: C{LBMember}
        @return {LBMember} Member after joining the balancer.
        """

        raise NotImplementedError, \
                'balancer_attach_member not implemented for this driver'

    def balancer_detach_member(self, balancer, member):
        """
        Detach member from balancer

        @return: C{bool} True if member detach was successful, otherwise False

        """

        raise NotImplementedError, \
                'balancer_detach_member not implemented for this driver'

    def balancer_list_members(self, balancer):
        """
        Return list of members attached to balancer

        @return: C{list} of L{LBNode}s

        """

        raise NotImplementedError, \
                'balancer_list_members not implemented for this driver'

    def _value_to_algorithm(self, value):
        """
        Return C{LBAlgorithm} based on the value.
        """
        try:
            return self._VALUE_TO_ALGORITHM_MAP[value]
        except KeyError:
            raise LibcloudError(value='Invalid value: %s' % (value),
                                driver=self)

    def _algorithm_to_value(self, algorithm):
        """
        Return value based in the algorithm (C{LBAlgorithm}).
        """
        try:
            return self._ALGORITHM_TO_VALUE_MAP[algorithm]
        except KeyError:
            raise LibcloudError(value='Invalid algorithm: %s' % (algorithm),
                                driver=self)