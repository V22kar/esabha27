from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView

from social.models import FollowUser,MyPost,MyProfile,PostComment,PostLike
from django.views.generic.detail import DetailView
from django.db.models import Q
from django.views.generic.edit import UpdateView,CreateView,DeleteView
from django.http.response import HttpResponseRedirect
import post

# Create your views here.

@method_decorator(login_required, name="dispatch")
class HomeView(TemplateView):
    template_name = "social/home.html"

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self,**kwargs)
        #context["name"] = "abcabcabc"
        followedlist = FollowUser.objects.filter(followed_by = self.request.user.myprofile) 
        followedlist2 = []
        for e in followedlist:
            followedlist2.append(e.profile)
        si = self.request.GET.get("si")
        if si == None:
            si = ""
        postlist = MyPost.objects.filter(Q(uploaded_by__in = followedlist2)).filter(Q(subject__icontains = si) | Q(msg__icontains = si)).order_by("id")
        print(postlist)

        for p1 in postlist:
            p1.liked =False
            ob = PostLike.objects.filter(post=p1, liked_by=self.request.user.myprofile)
            if ob:
                p1.liked= True

            ob = PostLike.objects.filter(post = p1)
            p1.likecount = ob.count()
        context["mypost_list"] = postlist
        return context

class AboutView(TemplateView):
    template_name = "social/about.html"

class ContactView(TemplateView):
    template_name = "social/contact.html"

@method_decorator(login_required, name="dispatch")
class MyProfileUpdateView(UpdateView):
    model = MyProfile
    fields =["name","age","address", "status","gender","phone_no","description","pic"]

@method_decorator(login_required, name="dispatch")
class MyPostCreateView(CreateView):
    model = MyPost
    fields =["subject","msg","pic"]

    def form_valid(self, form):
        self.object = form.save()
        self.object.uploaded_by = self.request.user.myprofile
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

@method_decorator(login_required, name="dispatch")
class MyPostListView(ListView):
    model = MyPost
    def get_queryset(self):
        si = self.request.GET.get("si")
        if si == None:
            si = ""
        return MyPost.objects.filter(Q(uploaded_by = self.request.user.myprofile)).filter(Q(subject__icontains = si) | Q(msg__icontains = si)).order_by("id")

@method_decorator(login_required, name="dispatch")
class MyPostDetailView(DetailView):
    model = MyPost

@method_decorator(login_required, name="dispatch")
class MyPostDeleteView(DeleteView):
    model = MyPost

@method_decorator(login_required, name="dispatch")
class MyProfileListView(ListView):
    model = MyProfile
    def get_queryset(self):
        si = self.request.GET.get("si")
        if si == None:
            si = ""
        proflist = MyProfile.objects.filter(name__icontains = si).order_by("id")
        for p1 in proflist:
            p1.followed =False
            ob = FollowUser.objects.filter(profile=p1, followed_by=self.request.user.myprofile)
            if ob:
                p1.followed= True
        return proflist


@method_decorator(login_required, name="dispatch")
class MyProfileDetailView(DetailView):
    model = MyProfile

#@method_decorator(login_required, name="dispatch")
def follow(request,pk):
    user = MyProfile.objects.get(pk=pk)
    FollowUser.objects.create(profile=user, followed_by=request.user.myprofile)
    return HttpResponseRedirect(redirect_to="/social/myprofile/")

#@method_decorator(login_required, name="dispatch")
def unfollow(request,pk):
    user = MyProfile.objects.get(pk=pk)
    FollowUser.objects.filter(profile = user, followed_by=request.user.myprofile).delete()
    return HttpResponseRedirect(redirect_to="/social/myprofile/")

#@method_decorator(login_required, name="dispatch")
def like(request,pk):
    post = MyPost.objects.get(pk=pk)
    PostLike.objects.create(post=post, liked_by=request.user.myprofile)
    return HttpResponseRedirect(redirect_to="/social/home/")

#@method_decorator(login_required, name="dispatch")
def unlike(request,pk):
    post = MyPost.objects.get(pk=pk)
    PostLike.objects.filter(post = post, liked_by=request.user.myprofile).delete()
    return HttpResponseRedirect(redirect_to="/social/home/")
