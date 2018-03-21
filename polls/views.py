'''Views for app polls'''
from django.shortcuts import render
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.template import loader
from django.shortcuts import get_object_or_404
from django.views import generic
from django.utils import timezone
from django.db import connection
import datetime
from .models import Flight, Airline, Customer
# from .models import Question_new, Choice_new


def index(request):
    '''Substitiued by IndexView, which is a template provide by Django'''
    # latest_question_list = Question_new.objects.order_by('-pub_date')[:5]
    latest_question_list = ""
    template = loader.get_template('polls/index.html')
    context = {
        'latest_question_list': latest_question_list,
    }
    return HttpResponse(template.render(context, request))


def search(request):
    '''
    Logic to search flight
    '''
    template = loader.get_template('polls/search.html')
    from_location = request.POST['from']
    print(type(from_location))
    to_location = request.POST['to']
    passenger = request.POST['passenger']
    leave_date = timezone.now(
    ) if request.POST['leave'] is None else request.POST['leave']
    leave_day = getDayFromDate(leave_date)
    return_date = (timezone.now() + datetime.timedelta(days=1)
                   ) if request.POST['return'] is None else request.POST['return']
    return_day = getDayFromDate(return_date)
    # result = Flight.objects.filter(depart_airport=from_location,
    #                                arrive_airport=to_location, workday__range=[leave_day, leave_day+10],)
    direct_result = Flight.objects.filter(depart_airport=from_location,
                                          arrive_airport=to_location, workday=(leave_day % 2),)
    one_stop_result = one_stop_flight(
        from_location, to_location, leave_day % 2, (leave_day+1) % 2)
    context = {
        'direct_flight': direct_result,
        'one_stop_flight': one_stop_result,
        'leave_date': leave_date,
        'return_date': return_date,
    }
    return HttpResponse(template.render(context, request))


def customer(request):
    template = loader.get_template('polls/customer.html')
    cus = Customer.objects.get(customer_id=19)
    context = {
        'customers': cus,
    }
    return HttpResponse(template.render(context, request))


def manager(request):
    template = loader.get_template('polls/manager_index.html')
    cus = Customer.objects.order_by('customer_id')
    context = {
        'customers': cus,
    }
    return HttpResponse(template.render(context, request))


def one_stop_flight(start, end, workday1, workday2):
    query = RAW_SQL_FLIGHT['ONE_STOP'].format(start_airport=start, end_airport=end, workday1=workday1,
                                              workday2=workday2)
    # print(query)
    return execute_custom_sql(query)


def execute_custom_sql(s):
    cursor = connection.cursor()
    cursor.execute(s)
    return cursor.fetchall()


RAW_SQL_FLIGHT = {
    'ONE_STOP': '''
                SELECT *
                FROM(
                SELECT f1.Airline_ID as f_airline_id, f1.Flight_ID as f_flight_id, f1.Fare as f_fare, f1.Depart_time as f_depart_time,
                f1.Depart_Airport as f_depart_airport, f1.Arrive_time as f_arrive_time, f1.Arrive_Airport as f_arrive_airport,
                f2.Airline_ID as s_airline_id, f2.Flight_ID as s_flight_id, f2.Fare as s_fare, f2.Depart_time as s_depart_time,
                f2.Depart_Airport as s_depart_airport, f2.Arrive_time as s_arrive_time, f2.Arrive_Airport as s_arrive_airport
                FROM Flight f1
                JOIN Flight f2
                WHERE f1.Arrive_Airport=f2.Depart_Airport
                AND f1.workday={workday1} AND f2.workday={workday2}
                ) res
                WHERE f_depart_airport="{start_airport}" AND s_arrive_airport="{end_airport}"
            ''',
}


def getDayFromDate(date):
    '''
    Get day from date like 2018-03-01
    '''
    day = date.split("-")[2]
    i = int(day)
    return i

# class IndexView(generic.ListView):  # pylint: disable=too-many-ancestors
#     """
#     New function, provided by Django, easier and short code
#     """
#     template_name = 'polls/index.html'
#     context_object_name = 'latest_question_list'

#     def get_queryset(self):
#         """
#         Return the last five published questions (not including those set to be
#         published in the future).
#         """
#         return Question_new.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]


# def detail(request, question_id):
#     '''Orignal function for detail page. Replaced by DetailView'''
#     question = get_object_or_404(Question_new, pk=question_id)
#     return render(request, 'polls/detail.html', {'question': question})
#  #      try:
#  #        question = Question_new.objects.get(pk=question_id)
#  #    except Question_new.DoesNotExist:
#  #        raise Http404("Question does not exist")
#  #    return render(request, 'polls/detail.html', {'question': question})


# class DetailView(generic.DetailView):  # pylint: disable=too-many-ancestors
#     '''
#     For detail page
#     '''
#     model = Question_new
#     template_name = 'polls/detail.html'

#     def get_queryset(self):
#         """
#         Excludes any questions that aren't published yet.
#         """
#         return Question_new.objects.filter(pub_date__lte=timezone.now())


# def results(request, question_id):
#     '''
#     Original for result page
#     '''
#     question = get_object_or_404(Question_new, pk=question_id)
#     return render(request, 'polls/results.html', {'question': question})


# class ResultsView(generic.DetailView):  # pylint: disable=too-many-ancestors
#     '''
#     For result page
#     '''
#     model = Question_new
#     template_name = 'polls/results.html'


# def vote(request, question_id):
#     '''
#     For vote page
#     '''
#     question = get_object_or_404(Question_new, pk=question_id)
#     try:
#         selected_choice = question.choice_new_set.get(
#             pk=request.POST['choice'])
#     except (KeyError, Choice_new.DoesNotExist):
#         # Redisplay the question voting form.
#         return render(request, 'polls/detail.html', {
#             'question': question,
#             'error_message': "You didn't select a Choice_new.",
#         })
#     else:
#         selected_choice.votes += 1
#         selected_choice.save()
#         # Always return an HttpResponseRedirect after successfully dealing
#         # with POST data. This prevents data from being posted twice if a
#         # user hits the Back button.
#         return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
