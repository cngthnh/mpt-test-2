#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from typing import List


class AssignmentState:
    CREATED = "created"
    LAUNCHED = "launched"
    ASSIGNED = "assigned"
    COMPLETED = "completed"
    ACCEPTED = "accepted"
    MIXED = "mixed"
    REJECTED = "rejected"
    EXPIRED = "expired"

    @staticmethod
    def valid() -> List[str]:
        """Return all valid assignment statuses"""
        # TODO write test to ensure all states are covered here
        return [
            AssignmentState.CREATED,
            AssignmentState.LAUNCHED,
            AssignmentState.ASSIGNED,
            AssignmentState.COMPLETED,
            AssignmentState.ACCEPTED,
            AssignmentState.MIXED,
            AssignmentState.REJECTED,
            AssignmentState.EXPIRED,
        ]

    @staticmethod
    def payable() -> List[str]:
        """Return all statuses that should be considered spent budget"""
        return [
            AssignmentState.LAUNCHED,
            AssignmentState.ASSIGNED,
            AssignmentState.COMPLETED,
            AssignmentState.ACCEPTED,
        ]

    @staticmethod
    def valid_unit() -> List[str]:
        """Return all statuses that are valids for a Unit"""
        return [
            AssignmentState.CREATED,
            AssignmentState.LAUNCHED,
            AssignmentState.ASSIGNED,
            AssignmentState.COMPLETED,
            AssignmentState.ACCEPTED,
            AssignmentState.REJECTED,
            AssignmentState.EXPIRED,
        ]

    @staticmethod
    def final_unit() -> List[str]:
        """Return all statuses that are terminal for a Unit"""
        return [AssignmentState.ACCEPTED, AssignmentState.EXPIRED]

    @staticmethod
    def final_agent() -> List[str]:
        """Return all statuses that are terminal changes to a Unit's agent"""
        return [
            AssignmentState.COMPLETED,
            AssignmentState.ACCEPTED,
            AssignmentState.REJECTED,
            AssignmentState.EXPIRED,
        ]
