from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from .models import Cat, Toy, Photo
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.generic.detail import DetailView
from django.views.generic import ListView
from .forms import FeedingForm
import boto3
import uuid

# Enviroment Variables
S3_BASE_URL = 'https://s3.us-east-1.amazonaws.com/'
BUCKET = 'cat-collector-persistence-teemy'

# Create your views here.

def signup(request):
    # handle POST Requests (signing up)
    error_message = ''
    if request.method == 'POST':
        # collect form inputs
        form = UserCreationForm(request.POST) # <= fills out the form with the form values from the request
        # validate form inputs
        if form.is_valid():
            # save the new user to the database
            user = form.save()
            # log the user in
            login(request, user)
            # redirect the user to the cats index
            return redirect('index')
        else:
        # if the user form is invalid - show an error message
            error_message = 'invalid credentials - please try again'
    # handle GET Requests (navigating the user to the signup page)
    # present the user with a fresh singup form
    form = UserCreationForm()
    context = {'form': form, 'error':error_message}
    return render(request, 'registration/signup.html', context)



def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

@login_required
def cats_index(request):
    cats = Cat.objects.filter(user=request.user)
    return render(request, 'cats/index.html', {'cats': cats})

# update this view function
@login_required
def cats_detail(request, cat_id):
  cat = Cat.objects.get(id=cat_id)
  if cat.user_id != request.user.id:
      return redirect('index')
  # Allows us to get all Toy objects and compares value between two lists
  toys_cat_doesnt_have = Toy.objects.exclude(id__in = cat.toys.all().values_list('id'))
  # instantiate FeedingForm to be rendered in the template
  feeding_form = FeedingForm()
  return render(request, 'cats/detail.html', {
    # include the cat and feeding_form in the context
    'cat': cat, 
    'feeding_form': feeding_form,
    # Add the toys to be displayed
    'toys': toys_cat_doesnt_have
  })

@login_required
def add_feeding(request, cat_id):
    # create the ModelForm using the data in request.POST
    form = FeedingForm(request.POST)
    #validate the from
    if form.is_valid():
        #don't save the form to the db until it has the cat_id assigned
        new_feeding = form.save(commit=False)
        new_feeding.cat_id = cat_id
        new_feeding.save()
    return redirect('detail', cat_id=cat_id)

@login_required
def assoc_toy(request, cat_id, toy_id):
    # Note that you can pass a toy's id instead of the whole object
    Cat.objects.get(id=cat_id).toys.add(toy_id)
    return redirect('detail', cat_id=cat_id)


@login_required
def add_photo(request, cat_id):
    # Collect the file asset from the request
    photo_file = request.FILES.get('photo-file', None)
    # check if file is present
    if photo_file:
        #create a reference to the s3 service from boto3
        s3 = boto3.client('s3')
        #create a unique identifier for each photo asset
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        # cute_cat.png => as214k.png
        try:
            #attempt to upload image to aws
            s3.upload_fileobj(photo_file, BUCKET, key)
            # dynamically generate photo url
            url = f"{S3_BASE_URL}{BUCKET}/{key}"
            # create an in-memory reference to a photo model instance
            photo = Photo(url=url, cat_id=cat_id)
            # save the instance to the database
            photo.save()

        except Exception as error:
            print('**********************')
            print('An error has occured with s3')
            print(error)
            print('**********************')
    
    return redirect('detail', cat_id=cat_id)






class CatCreate(LoginRequiredMixin, CreateView):
    model = Cat
    fields = ('name', 'breed', 'description', 'age')
    # success_url = '/cats/' 
    
    # This inherited method is called when a
     # valid cat form is being submitted
    def form_valid(self, form):
     # Assign the logged in user (self.request.user)
        form.instance.user = self.request.user  # form.instance is the cat
     # Let the CreateView do its job as usual
        return super().form_valid(form)

class CatUpdate( LoginRequiredMixin, UpdateView):
    model = Cat
    fields = ('breed', 'description', 'age')

class CatDelete(LoginRequiredMixin, DeleteView):
    model = Cat
    success_url = '/cats/'

class ToyCreate(LoginRequiredMixin, CreateView):
    model = Toy
    fields = ('name', 'color')

class ToyUpdate(LoginRequiredMixin, UpdateView):
    model = Toy
    fields = ('name', 'color')

class ToyDelete(LoginRequiredMixin, DeleteView):
    model = Toy
    success_url = '/toys/'

class ToyDetail(LoginRequiredMixin, DetailView):
    model = Toy
    template_name = 'toys/detail.html'

class ToyList(LoginRequiredMixin, ListView):
    model = Toy
    template_name = 'toys/index.html'