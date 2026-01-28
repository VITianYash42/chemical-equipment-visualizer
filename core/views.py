from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status, permissions, authentication # Added auth imports
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import pandas as pd
from .models import EquipmentFile

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    # 🔒 LOCK DOWN THE API
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
        file_obj = request.FILES['file']
        record = EquipmentFile.objects.create(file=file_obj)

        try:
            df = pd.read_csv(record.file.path)
            df.columns = df.columns.str.strip()

            stats = {
                "total_count": int(len(df)),
                "avg_flowrate": round(df['Flowrate'].mean(), 2),
                "avg_pressure": round(df['Pressure'].mean(), 2),
                "avg_temperature": round(df['Temperature'].mean(), 2),
                "type_distribution": df['Type'].value_counts().to_dict()
            }

            chart_data = {
                "equipment_names": df['Equipment Name'].tolist(),
                "flowrate": df['Flowrate'].tolist(),
                "pressure": df['Pressure'].tolist(),
                "temperature": df['Temperature'].tolist()
            }

            return Response({
                "message": "Analysis Successful",
                "file_id": record.id,
                "stats": stats,
                "chart_data": chart_data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class HistoryView(APIView):
    def get(self, request):
        files = EquipmentFile.objects.order_by('-uploaded_at')[:5]
        history = [{"id": x.id, "filename": x.file.name, "date": x.uploaded_at} for x in files]
        return Response(history)

class DownloadPDFView(APIView):
    # 🔒 Lock this too
    # authentication_classes = [authentication.BasicAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, file_id):
        try:
            record = EquipmentFile.objects.get(id=file_id)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="report_{file_id}.pdf"'
            
            p = canvas.Canvas(response, pagesize=letter)
            p.setFont("Helvetica-Bold", 16)
            p.drawString(100, 750, "Chemical Equipment Analysis Report")
            p.setFont("Helvetica", 12)
            p.drawString(100, 730, f"File ID: {record.id}")
            p.drawString(100, 715, f"Uploaded At: {str(record.uploaded_at)}")
            p.drawString(100, 680, "Analysis Complete.")
            p.showPage()
            p.save()
            return response
        except EquipmentFile.DoesNotExist:
            return Response({"error": "File not found"}, status=404)