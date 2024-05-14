from rest_framework_simplejwt.views import TokenObtainPairView
from users.serializers import CustomTokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework import status


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        tokens = CustomTokenObtainPairSerializer(request.data).validate(
            request.data,
        )
        return Response(tokens, status=status.HTTP_200_OK)
    

# @api_view(['GET'])
# @renderer_classes([JSONRenderer])
# @permission_classes([IsAuthenticated])
# def user_data(request):
#     logger.info('🔵 user_data')
#     try:
#         user = UserProfile.objects.get(user=request.user.id)
#         serializer = UserProfileModelSerializer(user)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     except Exception as err:
#         logger.error(traceback.format_exc())
#         return Response({}, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# @renderer_classes([JSONRenderer])
# def user_sign_in(request):
#     logger.info('🔵 user_sign_in')
#     try:
#         tokens = CustomTokenObtainPairSerializer(request.data).validate(
#             request.data,
#         )

#         profile = UserProfile.objects.filter(
#             email=request.data['email']).first()
#         serializer = UserProfileModelSerializer(profile)

#         return Response({
#             'user': serializer.data,
#             'refresh': str(tokens['refresh']),
#             'access': str(tokens['access']),
#         }, status=status.HTTP_200_OK)

#     except AuthenticationFailed:
#         return Response(appMsg.EMAIL_OR_PASS_INCORRECT, status=status.HTTP_401_UNAUTHORIZED)

#     except:
#         logger.error(traceback.format_exc())
#         return Response(appMsg.UNKNOWN_ERROR, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# @renderer_classes([JSONRenderer])
# def user_sign_up(request):
#     logger.info('🔵 user_sign_up')
#     try:
#         data = request.data.copy()

#         found_user = User.objects.filter(email=data['email']).first()
#         if found_user:
#             return Response(appMsg.EMAIL_EXISTS, status=status.HTTP_409_CONFLICT)
#         with transaction.atomic():
#             user_serializer = UserModelSerializer(data={
#                 'email': data['email'],
#                 'password': make_password(
#                     data['password'], salt=None, hasher='default'),
#             })
#             user_serializer.is_valid(raise_exception=True)
#             user_serializer.save()

#             profile_serializer = UserProfileModelSerializer(data={
#                 'email': data['email'],
#                 'user': user_serializer.data['id'],
#                 'english_level': data['english_level'],
#                 'verified': False,
#                 'screen_flow': True,
#             })
#             profile_serializer.is_valid(raise_exception=True)
#             profile_serializer.save()

#             device_serializer = DeviceModelSerializer(data={
#                 'uuid': data['uuid'],
#                 'user': user_serializer.data['id']
#             })
#             device_serializer.is_valid(raise_exception=True)
#             device_serializer.save()

#         class UserPayload:
#             id = user_serializer.data['id']

#         refresh = CustomTokenObtainPairSerializer().get_token(UserPayload)

#         return Response({
#             'user': profile_serializer.data,
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),
#         }, status=status.HTTP_201_CREATED)

#     except Exception as err:
#         logger.error(traceback.format_exc())
#         return Response(appMsg.UNKNOWN_ERROR, status=status.HTTP_400_BAD_REQUEST)

