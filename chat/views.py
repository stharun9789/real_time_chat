from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

# Track active users in private rooms
active_private_rooms = {}

@login_required
def home(request):
    """ Render the single index.html file for all cases """
    return render(request, "chat/index.html")

@login_required
def private_room(request, room_name):
    """ Handle private room access and limit to 2 users """
    global active_private_rooms

    if room_name not in active_private_rooms:
        active_private_rooms[room_name] = set()

    # Check if room is full (2 users max)
    if len(active_private_rooms[room_name]) >= 2:
        return JsonResponse({"error": "Room is full!"}, status=403)

    # Add user to room
    active_private_rooms[room_name].add(request.user.username)

    return render(request, "chat/private_room.html", {"room_name": room_name})

def leave_private_room(request, room_name):
    """ Remove user from private room when they leave """
    global active_private_rooms

    if room_name in active_private_rooms:
        active_private_rooms[room_name].discard(request.user.username)

        # Delete room if empty
        if not active_private_rooms[room_name]:
            del active_private_rooms[room_name]

    return redirect("home")
