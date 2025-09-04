from collections import defaultdict

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Player
from .serializers import PlayerSerializer


# Create your views here.
class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

    # get all player with filter option
    @action(detail=False, methods=['post'])
    def get_all(self, request):
        players = Player.objects.all()
        option = request.data
        club = option.get('club')
        position = option.get('position')
        if club:
            players = players.filter(club=club)
        if position:
            players = players.filter(position=position)
        serializer = PlayerSerializer(players, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # increase like api
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        player = self.get_object()
        player.likes += 1
        player.save()
        serializer = PlayerSerializer(player)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # reset all players like to 0
    @action(detail=False, methods=['post'])
    def reset_like(self, request):
        Player.objects.all().update(likes=0)
        return Response({"message": "All player likes have been reset"}, status=status.HTTP_200_OK)

    # get top liked players
    @action(detail=False, methods=['POST'])
    def ranking(self, request):
        ranking_type = request.data.get('type', 'overall')  # overall | by_position | by_club
        order = request.data.get('order', 'desc')
        reverse = order.lower() == 'desc'
        players = Player.objects.all()
        limit = request.data.get('limit', players.count())

        players = sorted(players, key=lambda x: x.likes, reverse=reverse)

        if ranking_type == 'overall':
            serializer = PlayerSerializer(players, many=True)
            return Response(serializer.data[:limit], status=status.HTTP_200_OK)

        elif ranking_type == 'by_position':
            grouped = defaultdict(list)
            for p in players:
                grouped[p.position].append(p)
            for pos in grouped:
                grouped[pos] = sorted(grouped[pos], key=lambda x: x.likes, reverse=reverse)

            grouped_serialized = {}
            for pos, group in grouped.items():
                serializer = PlayerSerializer(group, many=True)
                grouped_serialized[pos] = serializer.data

            flat_list = []
            for group in grouped_serialized.values():
                for player in group:
                    flat_list.append(player)

            if limit is not None:
                flat_list = flat_list[:limit]

            return Response(flat_list, status=status.HTTP_200_OK)


        elif ranking_type == 'by_club':

            grouped = defaultdict(list)

            for p in players:
                grouped[p.club].append(p)
            for club in grouped:
                grouped[club] = sorted(grouped[club], key=lambda x: x.likes, reverse=reverse)

            grouped_serialized = {}
            for club, group in grouped.items():
                serializer = PlayerSerializer(group, many=True)
                grouped_serialized[club] = serializer.data

            flat_list = []
            for group in grouped_serialized.values():
                for player in group:
                    flat_list.append(player)

            flat_list = flat_list[:limit]

            return Response(flat_list, status=status.HTTP_200_OK)

        else:
            return Response({[]}, status=status.HTTP_200_OK)

    # get top liked player in each club
    @action(detail=False, methods=['get'])
    def club_star(self, request):
        players = Player.objects.all()

        grouped = defaultdict(list)
        for p in players:
            grouped[p.club].append(p)

        for club in grouped:
            grouped[club] = sorted(grouped[club], key=lambda x: x.likes, reverse=True)

        top_players = []

        for group in grouped.values():
            if len(group) > 0:
                top_player = group[0]
                top_players.append(top_player)

        serializer = PlayerSerializer(top_players, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)