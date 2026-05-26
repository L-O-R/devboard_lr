from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Organization, OrgMembership
from .serializers import (
    OrganizationSerializer,
    OrgMembershipSerializer,
    InviteMemberSerializer
)
from .permissions import IsOrgMember, isOrgAdmin
from apps.accounts.models import User


#  create and list Org
class OrganizationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        org_ids = OrgMembership.objects.filter(
            user = request.user,
            is_active = True
        ).values_list('organization_id', flat=True)

        orgs = Organization.objects.filter(id__in = org_ids)
        seri = OrganizationSerializer(orgs, many= True)

        return Response(seri.data, status=status.HTTP_200_OK)
    
    def post (self, request):
        seri = OrganizationSerializer(data = request.data)

        if seri.is_valid():
            org = seri.save(created_by = request.user)

            OrgMembership.objects.create(
                user = request.user,
                organization = org,
                role = OrgMembership.Role.ORG_ADMIN,
            )

            return Response(
                OrganizationSerializer(org).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(seri.errors, status=status.HTTP_400_BAD_REQUEST)
    
#  org ddetails, view remove, delete
class OrganiztionDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated(), IsOrgMember()]
        return [IsAuthenticated(), isOrgAdmin()]

    def get(self, request, org_id):
        org = get_object_or_404(Organization, id=org_id)

        return Response(
            OrganizationSerializer(org).data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, org_id):
        org = get_object_or_404(Organization, id= org_id)
        serializer = OrganizationSerializer(
            org, data = request.data , partial = True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    def delete(self, request, org_id):
        org = get_object_or_404(Organization, id = org_id)
        org.delete()
        return Response(
            {'message': "deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
    

# list members 
class OrgMembersListView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]

    def get(self, request, org_id):
        memberships = OrgMembership.objects.filter(organization_id = org_id, is_active = True).select_related('user')

        serializer = OrgMembershipSerializer(memberships, many = True)

        return Response(serializer.data, status=status.HTTP_200_OK)

# invite members
class InviteMemberView(APIView):
    permission_classes = [IsAuthenticated, isOrgAdmin]

    def post(self, request, org_id):
        serializer = InviteMemberSerializer(data = request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            role = serializer.validated_data['role']

            user = User.objects.filter(email=email).first()
            org = get_object_or_404(Organization, id=org_id)

            if OrgMembership.objects.filter(user=user, organization=org, is_active=True).exists():
                return Response(
                    {'error': 'User is already a member of the organization.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            OrgMembership.objects.create(
                user = user,
                organization = org,
                role = role
            )

            return Response(
                {'message': f'{email} added as {role}.'},
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


# // remove member from org

class RemoveMemberView(APIView):
    permission_classes = [IsAuthenticated, isOrgAdmin]

    def delete(self, request, org_id, user_id):
        membership = get_object_or_404(
            OrgMembership,
            organization_id = org_id,
            user_id = user_id,
            is_active = True
        )

        if membership.user == request.user:
            return Response(
                {'error': 'You cannot remove yourself from the organization.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # membership.is_active = False
        # membership.save()

        # return Response(
        #     {'message': 'Member removed successfully.'},
        #     status=status.HTTP_200_OK
        # )

        membership.delete()
        return Response(
            {'message': 'Member removed successfully.'},
            status=status.HTTP_204_NO_CONTENT
        )

           