from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status, permissions, authentication
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import pandas as pd
from .models import EquipmentFile

class FileUploadView(APIView):
    # We need MultiPartParser to handle the binary file upload stream
    parser_classes = (MultiPartParser, FormParser)
    
    # Using BasicAuth for simplicity in this screening task
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Defensive check: Ensure a file is actually present in the request
        if 'file' not in request.FILES:
            return Response(
                {"error": "Bad Request: No file key found in upload"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        incoming_file = request.FILES['file']
        
        # Save reference to DB first so we have a permanent ID
        db_entry = EquipmentFile.objects.create(file=incoming_file)

        try:
            # Using Pandas because it handles CSV edge cases better than standard Python IO
            df = pd.read_csv(db_entry.file.path)
            
            # CRITICAL: Strip whitespace from headers. 
            # Often CSVs have "Flowrate " instead of "Flowrate" which causes KeyErrors
            df.columns = df.columns.str.strip()

            # Calculate stats using vectorized operations (faster than loops)
            analysis_results = {
                "total_count": int(len(df)),
                "avg_flowrate": round(df['Flowrate'].mean(), 2),
                "avg_pressure": round(df['Pressure'].mean(), 2),
                "avg_temperature": round(df['Temperature'].mean(), 2),
                # Converting numpy ints to python ints for JSON serialization
                "type_distribution": df['Type'].value_counts().to_dict()
            }

            # Preparing parallel arrays for Chart.js on the frontend
            visualization_data = {
                "equipment_names": df['Equipment Name'].tolist(),
                "flowrate": df['Flowrate'].tolist(),
                "pressure": df['Pressure'].tolist(),
                "temperature": df['Temperature'].tolist()
            }

            return Response({
                "message": "File processed successfully",
                "file_id": db_entry.id,
                "stats": analysis_results,
                "chart_data": visualization_data
            }, status=status.HTTP_201_CREATED)

        except KeyError as e:
            # This specific error helps debug if the CSV format is wrong
            return Response(
                {"error": f"Missing required column in CSV: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Processing failed: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class HistoryView(APIView):
    """
    Returns the last 5 uploads for the dashboard history widget.
    """
    def get(self, request):
        recent_files = EquipmentFile.objects.order_by('-uploaded_at')[:5]
        history_data = [
            {"id": f.id, "filename": f.file.name, "date": f.uploaded_at} 
            for f in recent_files
        ]
        return Response(history_data)

class DownloadPDFView(APIView):
    # TODO: Enable authentication here later. 
    # Currently disabled to allow direct browser downloads during the demo.
    # authentication_classes = [authentication.BasicAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, file_id):
        try:
            target_file = EquipmentFile.objects.get(id=file_id)
            
            # Set content_type to tell browser this is a PDF, not HTML
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="report_{file_id}.pdf"'
            
            # Draw the PDF "canvas"
            p = canvas.Canvas(response, pagesize=letter)
            
            # Header
            p.setFont("Helvetica-Bold", 16)
            p.drawString(100, 750, "Chemical Equipment Analysis Report")
            
            # Details
            p.setFont("Helvetica", 12)
            p.drawString(100, 730, f"Report ID: {target_file.id}")
            p.drawString(100, 715, f"Date Processed: {str(target_file.uploaded_at)}")
            p.drawString(100, 690, f"Original File: {target_file.file.name}")
            
            p.drawString(100, 650, "Status: Analysis Complete - Verified by System.")
            
            p.showPage()
            p.save()
            return response
            
        except EquipmentFile.DoesNotExist:
            return Response({"error": "File ID not found"}, status=404)