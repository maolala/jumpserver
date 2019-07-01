# -*- coding: utf-8 -*-
#

from functools import reduce
from rest_framework import serializers

from common.fields import StringManyToManyField
from orgs.mixins import BulkOrgResourceModelSerializer
from perms.models import AssetPermission, Action, ActionFlag
from assets.models import Node
from assets.serializers import AssetGrantedSerializer

__all__ = [
    'AssetPermissionCreateUpdateSerializer', 'AssetPermissionListSerializer',
    'AssetPermissionUpdateUserSerializer', 'AssetPermissionUpdateAssetSerializer',
    'AssetPermissionNodeSerializer', 'GrantedNodeSerializer',
    'NodeGrantedSerializer',
]


class ActionField(serializers.MultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = ActionFlag.CHOICES
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        return ActionFlag.value_to_choices(value)

    def to_internal_value(self, data):
        return ActionFlag.choices_to_value(data)


class ActionDisplayField(ActionField):
    def to_representation(self, value):
        values = super().to_representation(value)
        choices = dict(ActionFlag.CHOICES)
        return [choices.get(i) for i in values]


class AssetPermissionCreateUpdateSerializer(BulkOrgResourceModelSerializer):
    actions = ActionField()

    class Meta:
        model = AssetPermission
        exclude = ('created_by', 'date_created')


class AssetPermissionListSerializer(BulkOrgResourceModelSerializer):
    users = StringManyToManyField(many=True, read_only=True)
    user_groups = StringManyToManyField(many=True, read_only=True)
    assets = StringManyToManyField(many=True, read_only=True)
    nodes = StringManyToManyField(many=True, read_only=True)
    system_users = StringManyToManyField(many=True, read_only=True)
    actions = ActionDisplayField()
    is_valid = serializers.BooleanField()
    is_expired = serializers.BooleanField()

    class Meta:
        model = AssetPermission
        fields = '__all__'


class AssetPermissionUpdateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssetPermission
        fields = ['id', 'users']


class AssetPermissionUpdateAssetSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssetPermission
        fields = ['id', 'assets']


class AssetPermissionNodeSerializer(serializers.ModelSerializer):
    asset = AssetGrantedSerializer(required=False)
    assets_amount = serializers.SerializerMethodField()

    tree_id = serializers.SerializerMethodField()
    tree_parent = serializers.SerializerMethodField()

    class Meta:
        model = Node
        fields = [
            'id', 'key', 'value', 'asset', 'is_node', 'org_id',
            'tree_id', 'tree_parent', 'assets_amount',
        ]

    @staticmethod
    def get_assets_amount(obj):
        return obj.assets_amount

    @staticmethod
    def get_tree_id(obj):
        return obj.key

    @staticmethod
    def get_tree_parent(obj):
        return obj.parent_key


class NodeGrantedSerializer(serializers.ModelSerializer):
    """
    授权资产组
    """
    assets_granted = AssetGrantedSerializer(many=True, read_only=True)
    assets_amount = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = Node
        fields = [
            'id', 'key', 'name', 'value', 'parent',
            'assets_granted', 'assets_amount', 'org_id',
        ]

    @staticmethod
    def get_assets_amount(obj):
        return len(obj.assets_granted)

    @staticmethod
    def get_name(obj):
        return obj.name

    @staticmethod
    def get_parent(obj):
        return obj.parent.id


class GrantedNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = [
            'id', 'name', 'key', 'value',
        ]


# class GrantedAssetSerializer(serializers.ModelSerializer):
#     protocols = ProtocolSerializer(many=True)
#
#     class Meta:
#         model = Asset
#         fields = [
#             'id', 'hostname', 'ip', 'protocols', 'port', 'protocol',
#             'platform', 'domain', 'is_active', 'comment'
#         ]


# class GrantedSystemUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SystemUser
#         fields = [
#             'id', 'name', 'username', 'protocol', 'priority',
#             'login_mode', 'comment'
#         ]
