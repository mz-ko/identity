import logging
from typing import Dict, List, Tuple

from mongoengine import QuerySet
from spaceone.core.error import ERROR_INVALID_PARAMETER, ERROR_NOT_FOUND
from spaceone.core.manager import BaseManager

from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.model.workspace_group.database import WorkspaceGroup

_LOGGER = logging.getLogger(__name__)


class WorkspaceGroupManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workspace_group_model = WorkspaceGroup
        self.rb_mgr = RoleBindingManager()

    def create_workspace_group(self, params: dict) -> WorkspaceGroup:
        def _rollback(vo: WorkspaceGroup):
            _LOGGER.info(
                f"[create_workspace_group._rollback] Delete workspace group : {vo.workspace_group_id} ({vo.name})"
            )
            vo.delete()

        workspace_group_vo = self.workspace_group_model.create(params)
        self.transaction.add_rollback(_rollback, workspace_group_vo)

        return workspace_group_vo

    def update_workspace_group_by_vo(
        self, params: dict, workspace_group_vo: WorkspaceGroup
    ) -> WorkspaceGroup:
        def _rollback(old_data):
            _LOGGER.info(
                f"[update_workspace_group._rollback] Revert Data : {old_data['workspace_group_id']} ({old_data['name']})"
            )
            workspace_group_vo.update(old_data)

        self.transaction.add_rollback(_rollback, workspace_group_vo.to_dict())

        return workspace_group_vo.update(params)

    def delete_workspace_group_by_vo(self, workspace_group_vo: WorkspaceGroup) -> None:
        user_ids = [user["user_id"] for user in workspace_group_vo.users]
        rb_vos = self.rb_mgr.filter_role_bindings(
            user_id=user_ids,
            workspace_group_id=workspace_group_vo.workspace_group_id,
            domain_id=workspace_group_vo.domain_id,
        )

        if rb_vos.count() > 0:
            _LOGGER.debug(
                f"[delete_workspace_group_by_vo] Delete role bindings count with {workspace_group_vo.users}: {rb_vos.count()}"
            )
            for rb_vo in rb_vos:
                _LOGGER.debug(
                    f"[delete_workspace_group_by_vo] Delete role binding info: {rb_vo.to_dict()}"
                )
                rb_vo.delete()

        workspace_group_vo.delete()

    def get_workspace_group(
        self,
        workspace_group_id: str,
        domain_id: str,
        user_id: str = None,
    ) -> WorkspaceGroup:
        conditions = {
            "workspace_group_id": workspace_group_id,
            "domain_id": domain_id,
        }

        if user_id:
            conditions["users__user_id"] = user_id

        return self.workspace_group_model.get(**conditions)

    def filter_workspace_groups(self, **conditions) -> QuerySet:
        return self.workspace_group_model.filter(**conditions)

    def list_workspace_groups(self, query: dict) -> Tuple[QuerySet, int]:
        return self.workspace_group_model.query(**query)

    def stat_workspace_group(self, query: dict) -> dict:
        return self.workspace_group_model.stat(**query)

    @staticmethod
    def check_user_id_in_users(user_id: str, workspace_group_vo: WorkspaceGroup):
        return any(
            workspace_group_user_id == user_id
            for workspace_group_user_id in workspace_group_vo["users"]
        )

    def get_old_users_and_new_users(
        self, users: List[Dict[str, str]], workspace_group_id: str, domain_id: str
    ) -> Tuple[List[str], List[str]]:
        workspace_group_vo = self.get_workspace_group(workspace_group_id, domain_id)

        old_users = list(
            set(
                [user_info["user_id"] for user_info in workspace_group_vo.users]
                if workspace_group_vo.users
                else []
            )
        )
        new_users = list(set([user_info["user_id"] for user_info in users]))

        return old_users, new_users

    @staticmethod
    def check_new_users_already_in_workspace_group(
        old_users: List[str], new_users: List[str]
    ) -> None:
        if set(old_users) & set(new_users):
            _LOGGER.error(
                f"Users {new_users} is already in workspace group or not registered."
            )
            raise ERROR_INVALID_PARAMETER(
                key="users",
                reason=f"User {new_users} is already in the workspace group or not registered.",
            )

    @staticmethod
    def check_user_ids_exist_in_workspace_group(
        old_user_ids: List[str], user_ids: List[str]
    ) -> None:
        for user_id in user_ids:
            if user_id not in old_user_ids:
                _LOGGER.error(f"User ID {user_id} is not in workspace group.")
                raise ERROR_NOT_FOUND(key="user_id", value=user_id)
