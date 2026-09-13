import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from datetime import date, datetime, timedelta, timezone
from app.core.security import hash_password
from app.db.base import Base
from app.db.geometry import coords_to_point_wkt, polygon_geojson_to_wkt
from app.db.session import SessionLocal, engine
from app.models.enums import (
    UserRole,
    ComplianceCategory,
    ComplianceStatus,
    InspectionStatus,
    SeverityLevel,
    GrievanceCategory,
    GrievanceStatus,
    GrievancePriority,
    ActionStatus,
    DocumentOCRStatus,
    RiskLevel,
    NotificationChannel,
)
from app.models.organization import Organization, Subsidiary
from app.models.mine import Mine
from app.models.user import User, WorkerProfile
from app.models.contractor import Contractor, ContractorWorker
from app.models.compliance import ComplianceRequirement, ComplianceRecord
from app.models.inspection import Inspection, SafetyObservation
from app.models.corrective_action import CorrectiveAction
from app.models.grievance import Grievance
from app.models.attendance_wage import AttendanceRecord, WageRecord
from app.models.document import Document
from app.models.notification import Notification
from app.models.satellite import SatelliteObservation
from app.services.risk_service import AIRiskService
from app.services.audit_service import AuditService


def seed_database():
    """Populate database with 3 realistic fictional coal mines and complete operational records."""
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if already seeded
    if db.query(Organization).first():
        print("Database already contains data. Skipping seeding.")
        db.close()
        return

    print("Seeding Organizations and Subsidiaries...")
    # Apex Organization
    cil = Organization(
        name="Coal India Limited",
        code="CIL",
        description="Maharatna Public Sector Undertaking under the Ministry of Coal, Government of India.",
    )
    db.add(cil)
    db.commit()
    db.refresh(cil)

    # Subsidiaries
    mcl = Subsidiary(
        organization_id=cil.id,
        name="Mahanadi Coalfields Limited",
        code="MCL",
        state="Odisha",
    )
    ncl = Subsidiary(
        organization_id=cil.id,
        name="Northern Coalfields Limited",
        code="NCL",
        state="Madhya Pradesh",
    )
    ecl = Subsidiary(
        organization_id=cil.id,
        name="Eastern Coalfields Limited",
        code="ECL",
        state="West Bengal",
    )
    db.add_all([mcl, ncl, ecl])
    db.commit()
    db.refresh(mcl)
    db.refresh(ncl)
    db.refresh(ecl)

    print("Seeding Mines with Spatial Boundaries...")
    # Mine 1: Bharatpur Open Cast Project (MCL)
    bocp_poly = {
        "type": "Polygon",
        "coordinates": [
            [
                [85.140, 20.940],
                [85.165, 20.940],
                [85.165, 20.965],
                [85.140, 20.965],
                [85.140, 20.940],
            ]
        ],
    }
    mine_bharatpur = Mine(
        subsidiary_id=mcl.id,
        name="Bharatpur Open Cast Project",
        code="MCL-BOCP-01",
        location_name="Talcher Coalfield, Angul, Odisha",
        mine_type="OPEN_CAST",
        status="ACTIVE",
        boundary_geom=polygon_geojson_to_wkt(bocp_poly),
        center_lat=20.9525,
        center_lon=85.1525,
    )

    # Mine 2: Singrauli Underground Colliery (NCL)
    suc_poly = {
        "type": "Polygon",
        "coordinates": [
            [
                [82.670, 24.190],
                [82.695, 24.190],
                [82.695, 24.215],
                [82.670, 24.215],
                [82.670, 24.190],
            ]
        ],
    }
    mine_singrauli = Mine(
        subsidiary_id=ncl.id,
        name="Singrauli Underground Colliery",
        code="NCL-SUC-02",
        location_name="Singrauli Coal Basin, MP",
        mine_type="UNDERGROUND",
        status="ACTIVE",
        boundary_geom=polygon_geojson_to_wkt(suc_poly),
        center_lat=24.2025,
        center_lon=82.6825,
    )

    # Mine 3: Raniganj Deep Pit Mine (ECL)
    rdpm_poly = {
        "type": "Polygon",
        "coordinates": [
            [
                [87.110, 23.610],
                [87.135, 23.610],
                [87.135, 23.635],
                [87.110, 23.635],
                [87.110, 23.610],
            ]
        ],
    }
    mine_raniganj = Mine(
        subsidiary_id=ecl.id,
        name="Raniganj Deep Pit Mine",
        code="ECL-RDPM-03",
        location_name="Paschim Bardhaman, West Bengal",
        mine_type="MIXED",
        status="ACTIVE",
        boundary_geom=polygon_geojson_to_wkt(rdpm_poly),
        center_lat=23.6225,
        center_lon=87.1225,
    )

    db.add_all([mine_bharatpur, mine_singrauli, mine_raniganj])
    db.commit()
    db.refresh(mine_bharatpur)
    db.refresh(mine_singrauli)
    db.refresh(mine_raniganj)

    print("Seeding Users Across All 6 RBAC Roles...")
    users = [
        # System Admin
        User(
            email="admin@mineguard.gov.in",
            hashed_password=hash_password("Admin@12345"),
            full_name="Rajesh Kumar Verma (DGMS Admin)",
            role=UserRole.SYSTEM_ADMIN,
            phone_number="+91-9811001122",
            organization_id=cil.id,
        ),
        # Corporate Admin
        User(
            email="corporate@mineguard.gov.in",
            hashed_password=hash_password("Corp@12345"),
            full_name="Dr. Ananya Sen (CIL Director Safety)",
            role=UserRole.CORPORATE_ADMIN,
            phone_number="+91-9811003344",
            organization_id=cil.id,
        ),
        # Auditor
        User(
            email="auditor@mineguard.gov.in",
            hashed_password=hash_password("Audit@12345"),
            full_name="Vikramaditya Rao (Statutory Mine Auditor)",
            role=UserRole.AUDITOR,
            phone_number="+91-9811005566",
            organization_id=cil.id,
        ),
        # Mine Managers
        User(
            email="manager.bharatpur@mineguard.gov.in",
            hashed_password=hash_password("Password@123"),
            full_name="Sanjay Mohanty (Agent & Mine Manager)",
            role=UserRole.MINE_MANAGER,
            phone_number="+91-9871007788",
            organization_id=cil.id,
            subsidiary_id=mcl.id,
            mine_id=mine_bharatpur.id,
        ),
        User(
            email="manager.singrauli@mineguard.gov.in",
            hashed_password=hash_password("Password@123"),
            full_name="Pradeep Tripathi (Mine Manager)",
            role=UserRole.MINE_MANAGER,
            phone_number="+91-9871009900",
            organization_id=cil.id,
            subsidiary_id=ncl.id,
            mine_id=mine_singrauli.id,
        ),
        User(
            email="manager.raniganj@mineguard.gov.in",
            hashed_password=hash_password("Password@123"),
            full_name="Debabrata Banerjee (Mine Manager)",
            role=UserRole.MINE_MANAGER,
            phone_number="+91-9871001133",
            organization_id=cil.id,
            subsidiary_id=ecl.id,
            mine_id=mine_raniganj.id,
        ),
        # Field Inspectors
        User(
            email="inspector.bharatpur@mineguard.gov.in",
            hashed_password=hash_password("Password@123"),
            full_name="Pooja Sharma (DGMS Safety Inspector)",
            role=UserRole.FIELD_INSPECTOR,
            phone_number="+91-9822002233",
            organization_id=cil.id,
            subsidiary_id=mcl.id,
            mine_id=mine_bharatpur.id,
        ),
        User(
            email="inspector.singrauli@mineguard.gov.in",
            hashed_password=hash_password("Password@123"),
            full_name="Manoj K. Singh (Inspector of Mines)",
            role=UserRole.FIELD_INSPECTOR,
            phone_number="+91-9822004455",
            organization_id=cil.id,
            subsidiary_id=ncl.id,
            mine_id=mine_singrauli.id,
        ),
        # Workers
        User(
            email="worker.ramesh@mineguard.gov.in",
            hashed_password=hash_password("Password@123"),
            full_name="Ramesh Chandra Nayak",
            role=UserRole.WORKER,
            phone_number="+91-9733001122",
            organization_id=cil.id,
            subsidiary_id=mcl.id,
            mine_id=mine_bharatpur.id,
        ),
        User(
            email="worker.suresh@mineguard.gov.in",
            hashed_password=hash_password("Password@123"),
            full_name="Suresh Kumar Yadav",
            role=UserRole.WORKER,
            phone_number="+91-9733003344",
            organization_id=cil.id,
            subsidiary_id=ncl.id,
            mine_id=mine_singrauli.id,
        ),
        User(
            email="worker.amit@mineguard.gov.in",
            hashed_password=hash_password("Password@123"),
            full_name="Amit Mondal",
            role=UserRole.WORKER,
            phone_number="+91-9733005566",
            organization_id=cil.id,
            subsidiary_id=ecl.id,
            mine_id=mine_raniganj.id,
        ),
    ]

    db.add_all(users)
    db.commit()

    # Worker Profiles
    w_ramesh = db.query(User).filter(User.email == "worker.ramesh@mineguard.gov.in").first()
    w_suresh = db.query(User).filter(User.email == "worker.suresh@mineguard.gov.in").first()
    w_amit = db.query(User).filter(User.email == "worker.amit@mineguard.gov.in").first()

    wp1 = WorkerProfile(user_id=w_ramesh.id, employee_id="MCL-EMP-1049", trade="Heavy Dumper Operator", emergency_contact="+91-9733001100", blood_group="B+")
    wp2 = WorkerProfile(user_id=w_suresh.id, employee_id="NCL-EMP-2081", trade="Continuous Miner Mechanic", emergency_contact="+91-9733003300", blood_group="O+")
    wp3 = WorkerProfile(user_id=w_amit.id, employee_id="ECL-EMP-3112", trade="Safety Sirdar / Timberman", emergency_contact="+91-9733005500", blood_group="A+")
    db.add_all([wp1, wp2, wp3])
    db.commit()

    print("Seeding Compliance Requirements and Mine Records...")
    reqs = [
        ComplianceRequirement(
            title="Annual Slope Stability & Highwall Radar Audit",
            category=ComplianceCategory.SAFETY,
            description="Statutory geotechnical slope stability clearance for open cast benches under CMR 2017 Reg 106.",
            statutory_act="Coal Mines Regulations 2017, Regulation 106",
            frequency="ANNUAL",
        ),
        ComplianceRequirement(
            title="Continuous Underground Ventilation & Gas Monitoring Return",
            category=ComplianceCategory.SAFETY,
            description="Monthly air velocity and inflammable gas (CH4, CO) verification report.",
            statutory_act="Mines Act 1952, Section 22A",
            frequency="MONTHLY",
        ),
        ComplianceRequirement(
            title="Effluent Treatment & Ground Water Recharge Return",
            category=ComplianceCategory.ENVIRONMENT,
            description="State Pollution Control Board compliance on mine discharge water quality and settling ponds.",
            statutory_act="Water (Prevention and Control of Pollution) Act 1974",
            frequency="QUARTERLY",
        ),
        ComplianceRequirement(
            title="Contract Labour Statutory Minimum Wage Reconciliation",
            category=ComplianceCategory.LABOUR,
            description="Quarterly wage register audit ensuring high-skilled and unskilled wage compliance.",
            statutory_act="Contract Labour (Regulation and Abolition) Act 1970",
            frequency="QUARTERLY",
        ),
    ]
    db.add_all(reqs)
    db.commit()

    today = date.today()
    rec1 = ComplianceRecord(
        requirement_id=reqs[0].id,
        mine_id=mine_bharatpur.id,
        due_date=today + timedelta(days=20),
        status=ComplianceStatus.SUBMITTED,
        submission_date=datetime.now(timezone.utc),
        review_notes="Slope stability radar scans submitted. Under review by Director of Mines Safety.",
    )
    rec2 = ComplianceRecord(
        requirement_id=reqs[2].id,
        mine_id=mine_bharatpur.id,
        due_date=today - timedelta(days=10),
        status=ComplianceStatus.OVERDUE,
        review_notes="SPCB water analysis sample overdue.",
    )
    rec3 = ComplianceRecord(
        requirement_id=reqs[1].id,
        mine_id=mine_singrauli.id,
        due_date=today + timedelta(days=15),
        status=ComplianceStatus.APPROVED,
        submission_date=datetime.now(timezone.utc) - timedelta(days=5),
        review_notes="Ventilation survey verified by Principal Inspector.",
    )
    rec4 = ComplianceRecord(
        requirement_id=reqs[3].id,
        mine_id=mine_raniganj.id,
        due_date=today + timedelta(days=30),
        status=ComplianceStatus.PENDING,
    )
    db.add_all([rec1, rec2, rec3, rec4])
    db.commit()

    print("Seeding Inspections and Safety Observations...")
    insp_p = db.query(User).filter(User.email == "inspector.bharatpur@mineguard.gov.in").first()
    insp1 = Inspection(
        mine_id=mine_bharatpur.id,
        inspector_id=insp_p.id,
        inspection_type="ROUTINE_SAFETY",
        inspection_date=datetime.now(timezone.utc) - timedelta(days=2),
        latitude=20.9530,
        longitude=85.1530,
        geom=coords_to_point_wkt(20.9530, 85.1530),
        status=InspectionStatus.IN_PROGRESS,
        summary="Quarterly electrical safety and haul road gradient inspection.",
    )
    db.add(insp1)
    db.commit()
    db.refresh(insp1)

    obs1 = SafetyObservation(
        inspection_id=insp1.id,
        mine_id=mine_bharatpur.id,
        reporter_id=insp_p.id,
        title="Excessive Haul Road Berm Degradation at Bench 4",
        description="Safety berm height is under 1.5m, posing dumper overturn hazard on ramp 4B.",
        severity=SeverityLevel.HIGH,
        category="HAUL_ROAD",
        latitude=20.9532,
        longitude=85.1534,
        geom=coords_to_point_wkt(20.9532, 85.1534),
        status="OPEN",
    )
    obs2 = SafetyObservation(
        inspection_id=insp1.id,
        mine_id=mine_bharatpur.id,
        reporter_id=insp_p.id,
        title="Dust Suppression Mist Spray Malfunction",
        description="Transfer chute water nozzles choked with silt, causing visible coal dust emissions.",
        severity=SeverityLevel.MEDIUM,
        category="DUST_SUPPRESSION",
        latitude=20.9540,
        longitude=85.1520,
        geom=coords_to_point_wkt(20.9540, 85.1520),
        status="OPEN",
    )
    db.add_all([obs1, obs2])
    db.commit()
    db.refresh(obs1)

    ca1 = CorrectiveAction(
        safety_observation_id=obs1.id,
        inspection_id=insp1.id,
        mine_id=mine_bharatpur.id,
        description="Rebuild earthen safety berms to a minimum height of 2.0m along Bench 4 ramp.",
        due_date=today + timedelta(days=3),
        status=ActionStatus.IN_PROGRESS,
    )
    db.add(ca1)
    db.commit()

    print("Seeding Worker Grievances...")
    grv1 = Grievance(
        complaint_reference="MG-GRV-20260912-0001",
        worker_id=w_ramesh.id,
        mine_id=mine_bharatpur.id,
        category=GrievanceCategory.WORKPLACE_SAFETY,
        description="Dumper cab air conditioner defective and vibration dampers worn out, causing severe fatigue in 40C heat.",
        priority=GrievancePriority.HIGH,
        status=GrievanceStatus.UNDER_INVESTIGATION,
        is_confidential=False,
    )
    grv2 = Grievance(
        complaint_reference="MG-GRV-20260912-0002",
        worker_id=w_suresh.id,
        mine_id=mine_singrauli.id,
        category=GrievanceCategory.WAGE,
        description="Night shift overtime allowance for August 2026 not reflected in bank credit statement.",
        priority=GrievancePriority.MEDIUM,
        status=GrievanceStatus.PENDING,
        is_confidential=True,
    )
    db.add_all([grv1, grv2])
    db.commit()

    print("Seeding Attendance and Wage Records...")
    for day in range(1, 6):
        att = AttendanceRecord(
            worker_id=w_ramesh.id,
            mine_id=mine_bharatpur.id,
            date=today - timedelta(days=day),
            shift="SHIFT_1",
            status="PRESENT",
            check_in_time=datetime.now(timezone.utc) - timedelta(days=day, hours=8),
            check_out_time=datetime.now(timezone.utc) - timedelta(days=day),
        )
        db.add(att)

    wage = WageRecord(
        worker_id=w_ramesh.id,
        mine_id=mine_bharatpur.id,
        month=8,
        year=2026,
        base_amount=38500.0,
        overtime_amount=4200.0,
        deductions=1800.0,
        net_amount=40900.0,
        payment_status="PAID",
    )
    db.add(wage)
    db.commit()

    print("Seeding Satellite InSAR Subsidence Hotspots...")
    hotspots_rdpm = [
        {"latitude": 23.6230, "longitude": 87.1235, "rate_mm_year": -14.2, "status": "ACTIVE_SUBSIDENCE_CAUTION"},
        {"latitude": 23.6210, "longitude": 87.1215, "rate_mm_year": -8.5, "status": "MONITORED_DEFORMATION"},
    ]
    sat_rdpm = SatelliteObservation(
        mine_id=mine_raniganj.id,
        observation_date=today - timedelta(days=7),
        sensor="SENTINEL_1_SAR",
        subsidence_rate_mm_year=-14.2,
        risk_level=RiskLevel.MEDIUM,
        hotspot_coords_json=json.dumps(hotspots_rdpm),
        metadata_json=json.dumps({"orbit": "Descending Track 128", "wavelength_cm": 5.6, "coherence": 0.82}),
    )
    db.add(sat_rdpm)
    db.commit()

    print("Calculating Initial AI Risk Assessments...")
    AIRiskService.calculate_mine_risk(db, mine_bharatpur.id)
    AIRiskService.calculate_mine_risk(db, mine_singrauli.id)
    AIRiskService.calculate_mine_risk(db, mine_raniganj.id)

    print("Verifying Cryptographic Audit Trail...")
    audit_res = AuditService.verify_integrity(db)
    print("Audit Integrity Check Result:", audit_res["verification_message"])

    db.close()
    print("Database seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
