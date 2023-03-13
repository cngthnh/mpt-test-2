#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import time
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Mapping
from typing import Optional
from typing import TYPE_CHECKING
from uuid import uuid4

from omegaconf import MISSING

from mephisto.abstractions.providers.prolific import prolific_utils
from mephisto.abstractions.providers.prolific.prolific_utils import setup_credentials
from mephisto.data_model.requester import Requester
from mephisto.data_model.requester import RequesterArgs
from .provider_type import PROVIDER_TYPE

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB
    from mephisto.abstractions.providers.prolific.prolific_datastore import ProlificDatastore
    from omegaconf import DictConfig

MAX_QUALIFICATION_ATTEMPTS = 300


@dataclass
class ProlificRequesterArgs(RequesterArgs):
    name: str = field(
        default='prolific',
        metadata={
            'help': 'Name for the requester in the Mephisto DB.',
            'required': False,
        },
    )
    api_key: str = field(
        default=MISSING,
        metadata={
            'help': 'Prolific API key.',
            'required': True,
        },
    )


class ProlificRequester(Requester):
    """
    High level class representing a requester on some kind of crowd provider. Sets some default
    initializations, but mostly should be extended by the specific requesters for crowd providers
    with whatever implementation details are required to get those to work.
    """

    ArgsClass = ProlificRequesterArgs

    def __init__(
        self,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        super().__init__(db, db_id, row=row, _used_new_call=_used_new_call)
        self.datastore: "ProlificDatastore" = db.get_datastore_for_provider(PROVIDER_TYPE)

    def _get_client(self, requester_name: str) -> Any:
        """Get a Prolific client"""
        return self.datastore.get_client_for_requester(requester_name)

    def register(self, args: Optional["DictConfig"] = None) -> None:
        if args is not None:
            setup_credentials(self.requester_name, args)

    def is_registered(self) -> bool:
        """Return whether this requester has registered yet"""
        return prolific_utils.check_credentials(self.requester_name)

    def get_available_budget(self) -> float:
        return prolific_utils.check_balance()

    def create_new_qualification(self, qualification_name: str) -> str:
        """
        Create a new qualification on Prolific owned by the requester provided
        """
        client = self._get_client(self.requester_name)
        qualification_description = f'Equivalent qualification for {qualification_name}.'
        use_qualification_name = qualification_name
        qualification_id = prolific_utils.find_or_create_qualification(
            client, qualification_name, qualification_description
        )

        if qualification_id is None:
            # Try to append time to make the qualification unique
            use_qualification_name = f"{qualification_name}_{time.time()}"
            qualification_id = prolific_utils.find_or_create_qualification(
                client, use_qualification_name, qualification_description,
            )

            attempts = 0
            while qualification_id is None:
                # Append something somewhat random
                use_qualification_name = f"{qualification_name}_{str(uuid4())}"
                qualification_id = prolific_utils.find_or_create_qualification(
                    client, use_qualification_name, qualification_description,
                )
                attempts += 1
                if attempts > MAX_QUALIFICATION_ATTEMPTS:
                    raise Exception(
                        "Something has gone extremely wrong with creating qualification "
                        f"{qualification_name} for requester {self.requester_name}"
                    )

        # Store the new qualification in the datastore
        self.datastore.create_qualification_mapping(
            qualification_name, self.db_id, use_qualification_name, qualification_id,
        )
        return qualification_id

    @staticmethod
    def new(db: "MephistoDB", requester_name: str) -> "Requester":
        return ProlificRequester._register_requester(db, requester_name, PROVIDER_TYPE)
