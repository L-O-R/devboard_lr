from rest_framework import serializers
from .models import Organization, OrgMembership
from apps.accounts.serializers import UserProfileSerializer


class OrganizationSerializer(serializers.ModelSerializer):

    created_by = UserProfileSerializer(read_only = True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields= [
            'id', 'name', 'description', 
            'logo', 'created_by',
            'member_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']

    def get_member_count(self, obj):
        return obj.memberships.filter(is_active = True).count()
        
    
class OrgMembershipSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only = True)

    class Meta:
        model = OrgMembership
        fields = ['id', 'user', 'role', 'joined_at', 'is_active']
        read_only_feilds = ['id', 'user', 'joined_at']



class InviteMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgMembership
        fields = ['email', 'role']

    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=OrgMembership.Role.choices,
        default = OrgMembership.Role.DEVELOPER
    )

    def validate_emal(self, value):
        from apps.accounts.models import User
        if not User.objects.filter(email = value).exists():
            raise serializers.ValidationError(
                "No User found with this email!"
            )
        return value