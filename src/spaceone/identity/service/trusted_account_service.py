import logging
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.model.trusted_account.request import *
from spaceone.identity.model.trusted_account.response import *
from spaceone.identity.manager.schema_manager import SchemaManager
from spaceone.identity.manager.trusted_account_manager import TrustedAccountManager
from spaceone.identity.manager.workspace_manager import WorkspaceManager
from spaceone.identity.manager.secret_manager import SecretManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class TrustedAccountService(BaseService):
    resource = "TrustedAccount"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trusted_account_mgr = TrustedAccountManager()

    @transaction(
        permission="identity:TrustedAccount.write",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @convert_model
    def create(
        self, params: TrustedAccountCreateRequest
    ) -> Union[TrustedAccountResponse, dict]:
        """create trusted account

         Args:
            params (TrustedAccountCreateRequest): {
                'name': 'str',          # required
                'data': 'dict',         # required
                'provider': 'str',      # required
                'secret_schema_id': 'str',
                'secret_data': 'dict',
                'tags': 'dict',
                'resource_group': 'str',         # required
                'workspace_id': 'str',  # injected from auth
                'domain_id': 'str'      # injected from auth
            }

        Returns:
            TrustedAccountResponse:
        """

        # Check workspace
        if params.resource_group == "WORKSPACE":
            workspace_mgr = WorkspaceManager()
            workspace_mgr.get_workspace(params.workspace_id, params.domain_id)
        else:
            params.workspace_id = "*"

        # Check data by schema
        schema_mgr = SchemaManager()
        schema_mgr.validate_data_by_schema(
            params.provider, params.domain_id, "TRUSTED_ACCOUNT", params.data
        )

        trusted_account_vo = self.trusted_account_mgr.create_trusted_account(
            params.dict()
        )

        # Check secret_data by schema
        schema_mgr.validate_secret_data_by_schema_id(
            params.secret_schema_id, params.domain_id, params.secret_data
        )

        # Create a trusted secret
        secret_mgr = SecretManager()
        trusted_secret_info = secret_mgr.create_trusted_secret(
            {
                "name": f"{trusted_account_vo.trusted_secret_id}-trusted-secret",
                "data": params.secret_data,
                "schema_id": params.secret_schema_id,
                "trusted_account_id": trusted_account_vo.trusted_account_id,
                "resource_group": params.resource_group,
            }
        )

        # Update trusted_secret_id in trusted_account_vo
        trusted_account_vo = self.trusted_account_mgr.update_trusted_account_by_vo(
            {"trusted_secret_id": trusted_secret_info["trusted_secret_id"]},
            trusted_account_vo,
        )

        return TrustedAccountResponse(**trusted_account_vo.to_dict())

    @transaction(
        permission="identity:TrustedAccount.write",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @convert_model
    def update(
        self, params: TrustedAccountUpdateRequest
    ) -> Union[TrustedAccountResponse, dict]:
        """update trusted account

         Args:
            params (TrustedAccountUpdateRequest): {
                'trusted_account_id': 'str',    # required
                'name': 'str',
                'data': 'dict',
                'tags': 'dict',
                'workspace_id': 'str',          # injected from auth
                'domain_id': 'str'              # injected from auth
            }

        Returns:
            TrustedAccountResponse:
        """

        trusted_account_vo = self.trusted_account_mgr.get_trusted_account(
            params.trusted_account_id, params.domain_id, params.workspace_id
        )

        if params.data:
            # Check data by schema
            schema_mgr = SchemaManager()
            schema_mgr.validate_data_by_schema(
                trusted_account_vo.provider,
                params.domain_id,
                "TRUSTED_ACCOUNT",
                params.data,
            )

        trusted_account_vo = self.trusted_account_mgr.update_trusted_account_by_vo(
            params.dict(exclude_unset=True), trusted_account_vo
        )

        return TrustedAccountResponse(**trusted_account_vo.to_dict())

    @transaction(
        permission="identity:TrustedAccount.write",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @convert_model
    def update_secret_data(
        self, params: TrustedAccountUpdateSecretRequest
    ) -> Union[TrustedAccountResponse, dict]:
        """update trusted account secret data

         Args:
            params (TrustedAccountUpdateSecretRequest): {
                'trusted_account_id': 'str',    # required
                'secret_schema_id': 'str',      # required
                'secret_data': 'dict',          # required
                'workspace_id': 'str',          # injected from auth
                'domain_id': 'str'              # injected from auth
            }

        Returns:
            TrustedAccountResponse:
        """

        trusted_account_vo = self.trusted_account_mgr.get_trusted_account(
            params.trusted_account_id, params.domain_id, params.workspace_id
        )

        # Check secret_data by schema
        schema_mgr = SchemaManager()
        schema_mgr.validate_secret_data_by_schema_id(
            params.secret_schema_id,
            params.domain_id,
            params.secret_data,
        )

        # Update secret data
        secret_mgr = SecretManager()
        secret_mgr.update_trusted_secret_data(
            trusted_account_vo.trusted_secret_id,
            params.secret_schema_id,
            params.secret_data,
        )

        if trusted_account_vo.secret_schema_id != params.secret_schema_id:
            trusted_account_vo = self.trusted_account_mgr.update_trusted_account_by_vo(
                {"secret_schema_id": params.secret_schema_id}, trusted_account_vo
            )

        return TrustedAccountResponse(**trusted_account_vo.to_dict())

    @transaction(
        permission="identity:TrustedAccount.write",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @convert_model
    def delete(self, params: TrustedAccountDeleteRequest) -> None:
        """delete trusted account

         Args:
            params (TrustedAccountDeleteRequest): {
                'trusted_account_id': 'str',    # required
                'workspace_id': 'str',          # injected from auth
                'domain_id': 'str'              # injected from auth
            }

        Returns:
            None
        """

        trusted_account_vo = self.trusted_account_mgr.get_trusted_account(
            params.trusted_account_id, params.domain_id, params.workspace_id
        )

        # Delete trusted secret
        secret_mgr = SecretManager()
        secret_mgr.delete_trusted_secret(trusted_account_vo.trusted_secret_id)

        self.trusted_account_mgr.delete_trusted_account_by_vo(trusted_account_vo)

    @transaction(
        permission="identity:TrustedAccount.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @change_value_by_rule("APPEND", "workspace_id", "*")
    @convert_model
    def get(
        self, params: TrustedAccountGetRequest
    ) -> Union[TrustedAccountResponse, dict]:
        """get trusted account

         Args:
            params (TrustedAccountGetRequest): {
                'trusted_account_id': 'str',    # required
                'workspace_id': 'list',         # injected from auth
                'domain_id': 'str'              # injected from auth
            }

        Returns:
            TrustedAccountResponse:
        """

        trusted_account_vo = self.trusted_account_mgr.get_trusted_account(
            params.trusted_account_id, params.domain_id, params.workspace_id
        )

        return TrustedAccountResponse(**trusted_account_vo.to_dict())

    @transaction(
        permission="identity:TrustedAccount.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @change_value_by_rule("APPEND", "workspace_id", "*")
    @append_query_filter(
        [
            "trusted_account_id",
            "name",
            "provider",
            "secret_schema_id",
            "trusted_secret_id",
            "workspace_id",
            "domain_id",
        ]
    )
    @append_keyword_filter(["trusted_account_id", "name"])
    @convert_model
    def list(
        self, params: TrustedAccountSearchQueryRequest
    ) -> Union[TrustedAccountsResponse, dict]:
        """list trusted accounts

        Args:
            params (TrustedAccountSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'trusted_account_id': 'str',
                'name': 'str',
                'provider': 'str',
                'secret_schema_id': 'str',
                'trusted_secret_id': 'str',
                'workspace_id': 'list',     # injected from auth
                'domain_id': 'str',         # injected from auth
            }

        Returns:
            TrustedAccountsResponse:
        """

        query = params.query or {}
        (
            trusted_account_vos,
            total_count,
        ) = self.trusted_account_mgr.list_trusted_accounts(query)

        trusted_accounts_info = [
            trusted_account_vo.to_dict() for trusted_account_vo in trusted_account_vos
        ]
        return TrustedAccountsResponse(
            results=trusted_accounts_info, total_count=total_count
        )

    @transaction(
        permission="identity:TrustedAccount.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @change_value_by_rule("APPEND", "workspace_id", "*")
    @append_query_filter(["workspace_id", "domain_id"])
    @append_keyword_filter(["trusted_account_id", "name"])
    @convert_model
    def stat(self, params: TrustedAccountStatQueryRequest) -> dict:
        """stat trusted accounts

        Args:
            params (TrustedAccountStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'workspace_id': 'list',     # injected from auth
                'domain_id': 'str',         # injected from auth
            }

        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }

        """

        query = params.query or {}
        return self.trusted_account_mgr.stat_trusted_accounts(query)
