from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from pytube import YouTube
from django.conf import settings
import os
import assemblyai as aai
import openai
from .models import BlogPost

# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)


        # get yt title
        title = yt_title(yt_link)

        # get transcript
        transcription = get_transcription(yt_link)
        if not transcription:
            return JsonResponse({'error': " Failed to get transcript"}, status=500)


        # use OpenAI to generate the blog
        blog_content = generate_blog_from_transcription(transcription)
        if not blog_content:
            return JsonResponse({'error': " Failed to generate blog article"}, status=500)

        # save blog article to database
        new_blog_article = BlogPost.objects.create(
            user=request.user,
            youtube_title=title,
            youtube_link=yt_link,
            generated_content=blog_content,
        )
        new_blog_article.save()

        # return blog article as a response
        return JsonResponse({'content': blog_content})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def yt_title(link):
    try:
        yt = YouTube(link)
        title = yt.title
        return title
    except Exception as e:
        print(f"Error occurred while fetching YouTube title: {e}")
        return None


def download_audio(link):
    try:
        yt = YouTube(link)
        video = yt.streams.filter(only_audio=True).first()
        out_file = video.download(output_path=settings.MEDIA_ROOT)
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        os.rename(out_file, new_file)
        return new_file
    except Exception as e:
        print(f"Error occurred while downloading audio: {e}")
        return None

def get_transcription(link):
    try:
        audio_file = download_audio(link)
        if not audio_file:
            return None
        
        aai.settings.api_key = "7504266a887b41848799fd1d7c5dc00b"
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file)
        return transcript.text
    except Exception as e:
        print(f"Error occurred while transcribing audio: {e}")
        return None
    
def generate_blog_from_transcription(transcription):
    try:
        openai.api_key = "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"
        prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article, write it based on the transcript, but dont make it look like a youtube video, make it look like a proper blog article:\n\n{transcription}\n\nArticle:"
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=1000
        )
        generated_content = response.choices[0].text.strip()
        return generated_content
    except Exception as e:
        print(f"Error occurred while generating blog content: {e}")
        return None
    
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return redirect('/')
        else:
            # Return an 'invalid login' error message.
            return render(request, 'login.html', {'error_message': 'Invalid username or password'})
    else:
        return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirmPassword']

        if password == confirm_password:
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                error_message = 'Username already exists'
                return render(request, 'signup.html', {'error_message': error_message})
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                error_message = 'Email already exists'
                return render(request, 'signup.html', {'error_message': error_message})

            # Create the user (password will be automatically hashed)
            user = User.objects.create_user(username=username, email=email, password=password)
            # Log the user in after signup
            login(request, user)
            return redirect('/')
        else:
            error_message = 'Passwords do not match'
            return render(request, 'signup.html', {'error_message': error_message})
        
    return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('login') 