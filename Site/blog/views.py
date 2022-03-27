from django.shortcuts import render

posts = [
	{
		'author': 'in a',
		'title': 'Cat',
		'content': 'hat',
		'date_posted': 'August 27, 2020'
		}

]


def home(request):
	context = {
		'posts': posts
	}
	return render(request, 'blog/home.html', context)

def about(request):
	return render(request, 'blog/about.html', {'title': 'About'})


