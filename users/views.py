from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import ContactForm, CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("signup")
    template_name = "signup.html"


def user_contact(request):

    if request.method == "POST":

        form = ContactForm(request.POST)

        if form.is_valid():

            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["body"]
            form.save()

            return redirect("/thank-you/")

        return render(request, "contact.html", {"form": form})

    form = ContactForm()
    return render(request, "contact.html", {"form": form})
