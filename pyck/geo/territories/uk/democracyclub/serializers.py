from rest_framework import serializers


class PersonSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    url = serializers.URLField()
    name = serializers.CharField()


class PartySerializer(serializers.Serializer):
    id = serializers.CharField()
    url = serializers.URLField()


class PostSerializer(serializers.Serializer):
    id = serializers.CharField()
    url = serializers.URLField()
    label = serializers.CharField()
    slug = serializers.CharField()


class OrganizationSummarySerializer(serializers.Serializer):
    id = serializers.CharField()
    url = serializers.URLField()
    name = serializers.CharField()


class ElectionSummarySerializer(serializers.Serializer):
    id = serializers.CharField()
    url = serializers.URLField()
    name = serializers.CharField()


class MembershipSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    url = serializers.URLField()
    label = serializers.CharField()
    role = serializers.CharField()
    elected = serializers.BooleanField()
    person = PersonSerializer()
    on_behalf_of = PartySerializer()
    post = PostSerializer()
    start_date = serializers.DateSerializer(required=False)
    end_date = serializers.DateSerializer(required=False)
    election = ElectionSummarySerializer()


class CandidateResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    url = serializers.URLField()
    membership = MembershipSerializer()
    result_set = serializers.URLField()
    num_ballots = serializers.IntegerField()
    is_winner = serializers.BooleanField()


class ElectionSerializer(serializers.Serializer):
    id = serializers.CharField()
    url = serializers.URLField()
    name = serializers.CharField()
    winner_membership_role = serializers.CharField()
    candidate_membership_role = serializers.CharField()
    election_date = serializers.DateField()
    current = serializers.BooleanField()
    use_for_candidate_suggestions = serializers.BooleanField()
    organization = OrganizationSummarySerializer()
    party_lists_in_use = serializers.BooleanField()
    default_party_list_members_to_show = serializers.IntegerField()
    party_lists_in_use = serializers.BooleanField()
    show_official_documents = serializers.BooleanField()
    ocd_division = serializers.CharField()
    description = serializers.CharField()


class ResultSetSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    url = serializers.URLField()
    candidate_results = CandidateResultSerializer(many=True)
