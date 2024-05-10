# Original views
class AEConsultationWaitRoomView(DoctorRequiredMixin, ListView):
    ...

# Replaced by
class AEConsultationWaitRoomView(ClinicListView):
    template_name = 'ehr/clinic/ae_list.html'
    status_filter = 'waiting_for_consultation'
    clinic_filter = "A & E"
    room_filter = None

# Original views  
class AERoom1View(DoctorRequiredMixin, ListView):
    ...

# Replaced by
class AERoom1View(ClinicListView):
    template_name = 'ehr/clinic/ae_room1.html'
    status_filter = 'waiting_for_consultation'
    clinic_filter = "A & E"
    room_filter = 'ROOM 1'

# Original views
class AERoom2View(DoctorRequiredMixin, ListView):
    ...

# Replaced by (assuming you need this view)
class AERoom2View(ClinicListView):
    template_name = 'ehr/clinic/ae_room2.html'
    status_filter = 'waiting_for_consultation'
    clinic_filter = "A & E"
    room_filter = 'ROOM 2'

# Original views
class SOPDConsultationWaitRoomView(DoctorRequiredMixin, ListView):
    ...

# Replaced by
class SOPDConsultationWaitRoomView(ClinicListView):
    template_name = 'ehr/clinic/sopd_list.html'
    status_filter = 'waiting_for_consultation'
    clinic_filter = "SOPD"
    room_filter = None

# Original views
class AEConsultationFinishView(ListView):
    ...

# Replaced by
class AEConsultationFinishView(ClinicListView):
    template_name = 'ehr/doctor/patient_seen.html'
    status_filter = 'seen_by_doctor'
    clinic_filter = 'A & E'
    room_filter = None

# Original views
class AEAwaitingReviewView(ListView):
    ...

# Replaced by
class AEAwaitingReviewView(ClinicListView):
    template_name = 'ehr/doctor/review_patient.html'
    status_filter = 'awaiting_review'
    clinic_filter = 'A & E'
    room_filter = None

# Original views
class SOPDConsultationFinishView(ListView):
    ...

# Replaced by
class SOPDConsultationFinishView(ClinicListView):
    template_name = 'ehr/doctor/patient_seen.html'
    status_filter = 'seen_by_doctor'
    clinic_filter = 'SOPD'
    room_filter = None

# Original views
class SOPDAwaitingReviewView(ListView):
    ...

# Replaced by
class SOPDAwaitingReviewView(ClinicListView):
    template_name = 'ehr/doctor/review_patient.html'
    status_filter = 'awaiting_review'
    clinic_filter = 'SOPD'
    room_filter = None