from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import ShortenedURL
import validators

# Create your views here.
def home(request):
    recent_urls = ShortenedURL.objects.all().order_by('-created_at')[:10]
    
    if request.method == 'POST':
        original_url = request.POST.get('original_url', '').strip()
        custom_code = request.POST.get('custom_code', '').strip()
        
        if not original_url:
            messages.error(request, "Please enter a URL")
            return redirect('home')
            
        # Validate URL
        if not validators.url(original_url):
            messages.error(request, "Please enter a valid URL")
            return redirect('home')
            
        # Generate or use custom short code
        if custom_code:
            if ShortenedURL.objects.filter(short_code=custom_code).exists():
                messages.error(request, "This custom code is already in use")
                return redirect('home')
            short_code = custom_code
        else:
            short_code = ShortenedURL.generate_short_code()
        
        # Create and save the shortened URL
        shortened_url = ShortenedURL(
            original_url=original_url,
            short_code=short_code
        )
        shortened_url.save()

        short_url = request.build_absolute_uri(reverse('redirect', args=[short_code]))
        messages.success(request, f'Your shortened URL: <a href="{short_url}" target="_blank">{short_url}</a>')
        return redirect('home')

    return render(request, 'home.html', {
        'recent_urls': recent_urls
    })

def delete_url(request, short_code):
    if request.method == 'POST':
        url = get_object_or_404(ShortenedURL, short_code=short_code)
        url.delete()
        messages.success(request, f'URL {short_code} has been deleted.')
    return redirect('home')

def redirect_to_original(request, short_code):
    shortened_url = get_object_or_404(ShortenedURL, short_code=short_code)
    shortened_url.increment_visit_count()
    return redirect(shortened_url.original_url)

def stats(request, short_code):
    shortened_url = get_object_or_404(ShortenedURL, short_code=short_code)
    return render(request, 'stats.html', {'url': shortened_url})