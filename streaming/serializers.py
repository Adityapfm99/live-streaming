# streaming/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Stream, Donation, Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class StreamSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = Stream
        fields = ['id', 'title', 'description', 'created_at', 'user', 'username', 'video', 'is_active']  # List specific fields here
        
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'username', 'content', 'stream', 'created_at']
        read_only_fields = ['username']

    def create(self, validated_data):
        request = self.context.get('request')
        username = request.user.username
        stream = validated_data.pop('stream')
        comment = Comment.objects.create(stream=stream, username=username, **validated_data)
        return comment