import csv
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.apps import apps
from django.core import serializers
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from io import TextIOWrapper

from .models import TypeWorkout, Workout, Exercice, OneExercice
from home.models import Tag, Projet, Testimonial


@staff_member_required
def admin_dashboard(request):
    """Admin dashboard for managing all models"""
    
    # Get all models and their data counts
    models_data = {
        'workout': {
            'TypeWorkout': {
                'model': TypeWorkout,
                'count': TypeWorkout.objects.count(),
                'app': 'workout'
            },
            'Workout': {
                'model': Workout,
                'count': Workout.objects.count(),
                'app': 'workout'
            },
            'Exercice': {
                'model': Exercice,
                'count': Exercice.objects.count(),
                'app': 'workout'
            },
            'OneExercice': {
                'model': OneExercice,
                'count': OneExercice.objects.count(),
                'app': 'workout'
            }
        },
        'home': {
            'Tag': {
                'model': Tag,
                'count': Tag.objects.count(),
                'app': 'home'
            },
            'Projet': {
                'model': Projet,
                'count': Projet.objects.count(),
                'app': 'home'
            },
            'Testimonial': {
                'model': Testimonial,
                'count': Testimonial.objects.count(),
                'app': 'home'
            }
        }
    }
    
    context = {
        'models_data': models_data,
        'page': 'admin_dashboard'
    }
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
def export_model_data(request, app_name, model_name):
    """Export model data as CSV or JSON"""
    format_type = request.GET.get('format', 'csv')
    
    try:
        model = apps.get_model(app_name, model_name)
        data = model.objects.all()
        
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{model_name}.csv"'
            
            writer = csv.writer(response)
            
            # Get field names
            field_names = [field.name for field in model._meta.fields]
            writer.writerow(field_names)
            
            # Write data
            for obj in data:
                row = []
                for field_name in field_names:
                    value = getattr(obj, field_name)
                    if hasattr(value, 'pk'):  # Foreign key
                        value = value.pk
                    row.append(value)
                writer.writerow(row)
            
            return response
            
        elif format_type == 'json':
            response = HttpResponse(content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{model_name}.json"'
            
            # Serialize the data
            serialized_data = serializers.serialize('json', data)
            response.write(serialized_data)
            
            return response
            
    except Exception as e:
        messages.error(request, f'Error exporting {model_name}: {str(e)}')
        return redirect('admin_dashboard')


@staff_member_required
@csrf_exempt
def import_model_data(request, app_name, model_name):
    """Import model data from CSV or JSON"""
    if request.method == 'POST':
        try:
            model = apps.get_model(app_name, model_name)
            uploaded_file = request.FILES['file']
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            with transaction.atomic():
                if file_extension == 'csv':
                    file_data = TextIOWrapper(uploaded_file.file, encoding=request.encoding)
                    csv_reader = csv.DictReader(file_data)
                    
                    for row in csv_reader:
                        # Handle foreign key fields
                        cleaned_row = {}
                        for field_name, value in row.items():
                            if value == '':
                                cleaned_row[field_name] = None
                            else:
                                # Check if it's a foreign key field
                                try:
                                    field = model._meta.get_field(field_name)
                                    if field.related_model:
                                        if value and value != 'None':
                                            cleaned_row[field_name + '_id'] = int(value)
                                    else:
                                        cleaned_row[field_name] = value
                                except:
                                    cleaned_row[field_name] = value
                        
                        # Remove id if present to create new objects
                        if 'id' in cleaned_row:
                            del cleaned_row['id']
                            
                        model.objects.create(**cleaned_row)
                
                elif file_extension == 'json':
                    file_content = uploaded_file.read().decode('utf-8')
                    data = json.loads(file_content)
                    
                    for item in data:
                        fields = item.get('fields', {})
                        # Remove id to create new objects
                        model.objects.create(**fields)
            
            messages.success(request, f'Successfully imported data for {model_name}')
            
        except Exception as e:
            messages.error(request, f'Error importing {model_name}: {str(e)}')
    
    return redirect('admin_dashboard')


@staff_member_required
def delete_all_model_data(request, app_name, model_name):
    """Delete all data for a specific model"""
    if request.method == 'POST':
        try:
            model = apps.get_model(app_name, model_name)
            count = model.objects.count()
            model.objects.all().delete()
            messages.success(request, f'Successfully deleted {count} {model_name} records')
        except Exception as e:
            messages.error(request, f'Error deleting {model_name}: {str(e)}')
    
    return redirect('admin_dashboard')


@staff_member_required
def get_model_data(request, app_name, model_name):
    """Get model data as JSON for display"""
    try:
        model = apps.get_model(app_name, model_name)
        data = model.objects.all()
        
        # Convert to list of dictionaries
        result = []
        field_names = []
        
        # Get all fields including ManyToMany
        for field in model._meta.fields:
            field_names.append(field.name)
        
        # Add ManyToMany fields
        for field in model._meta.many_to_many:
            field_names.append(field.name)
        
        for obj in data:
            obj_data = {'id': obj.pk}
            for field_name in field_names:
                try:
                    field = model._meta.get_field(field_name)
                    if field.many_to_many:
                        # Handle ManyToMany fields
                        m2m_values = getattr(obj, field_name).all()
                        obj_data[field_name] = ', '.join([str(item) for item in m2m_values])
                    else:
                        value = getattr(obj, field_name)
                        if value is None:
                            obj_data[field_name] = None
                        elif hasattr(value, 'pk'):  # Foreign key
                            obj_data[field_name] = str(value)
                        elif hasattr(value, 'strftime'):  # Date/DateTime field
                            obj_data[field_name] = value.strftime('%Y-%m-%d')
                        elif isinstance(value, (str, int, float, bool)):
                            obj_data[field_name] = value
                        else:
                            obj_data[field_name] = str(value)
                except Exception as field_error:
                    obj_data[field_name] = f"Error: {str(field_error)}"
            result.append(obj_data)
        
        return JsonResponse({
            'data': result,
            'fields': field_names,
            'count': len(result)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)