# Eko Solar Training Examples

These examples are imported from the local training dataset and reflect target workflows, outputs, and business conventions.

## Example 1: Create a CRM entry for a new solar lead from website form

### Input

Source: Website quote request form, Name: James Williams, Phone: 678-555-0192, Email: james.w@email.com, Address: 1450 Briarcliff Rd NE, Atlanta GA 30306, Service type: Residential solar, Notes: 2-story home, south roof, electric bill ~$200/month, interested in battery backup, flexible on timing

### Output

```json
{
  "action": "create_crm_entry",
  "data": {
    "customer_id": "ES-2024-0891",
    "name": "James Williams",
    "phone": "678-555-0192",
    "email": "james.w@email.com",
    "address": "1450 Briarcliff Rd NE, Atlanta GA 30306",
    "lead_source": "Website Form",
    "service_type": "Residential Solar",
    "estimated_size": "10-12kW",
    "battery_interest": true,
    "roof_type": "2-story, south-facing",
    "shade_analysis": "TBD - site survey needed",
    "status": "New Lead",
    "priority": "Medium",
    "assigned_to": "Sales",
    "next_action": "Schedule site survey",
    "created_date": "2024-06-14",
    "estimated_close_date": "2024-08-30",
    "google_calendar_event": "Pending - survey scheduling",
    "pipeline_stage": "Lead"
  }
}
```

## Example 2: Create a job entry for a solar installation project

### Input

Customer: Patricia Martinez, Contract signed: June 5, System: 8.5kW with 1 Tesla Powerwall 3, Deposit received: $14,000, Equipment ordered: REC Alpha Pure 400W (22 panels), SolarEdge SE10000H inverter, Permits: Dekalb County - submitted June 8, Installation target: July 15-20

### Output

```json
{
  "action": "create_job",
  "data": {
    "job_id": "JOB-2024-0456",
    "customer": "Patricia Martinez",
    "contract_date": "2024-06-05",
    "system_size": "8.5kW",
    "equipment": {
      "panels": "REC Alpha Pure 400W x22",
      "inverter": "SolarEdge SE10000H",
      "battery": "Tesla Powerwall 3 x1"
    },
    "contract_value": 28000.0,
    "deposit_received": 14000.0,
    "balance_due": 14000.0,
    "pipeline_stage": "Permits",
    "permit_status": {
      "county": "Dekalb",
      "submitted": "2024-06-08",
      "status": "Under Review",
      "expected_approval": "2024-06-25"
    },
    "installation_window": "2024-07-15 to 2024-07-20",
    "subcontractor": "TBD",
    "photo_docs": [],
    "google_calendar_sync": true,
    "square_invoicing": true,
    "next_action": "Follow up on permit status June 22",
    "notes": "Customer prefers morning install. HOA approval obtained June 3."
  }
}
```

## Example 3: Generate an itemized solar quote with deposit and Square payment link

### Input

Customer: David Chen, System: 12kW residential, Panel: Q.Cells Q.PEAK DUO BLK ML-G10+ 400W (30 panels), Inverter: Enphase IQ8+ (30 microinverters), Battery: 2x Tesla Powerwall 3, Roof: Asphalt shingle, standard install, Financing: Cash purchase, Location: Sandy Springs GA

### Output

```json
{"action": "generate_quote", "quote_id": "QTE-2024-0567", "customer": "David Chen", "date": "2024-06-14", "valid_until": "2024-07-14", "line_items": [{"category": "Solar Panels", "item": "Q.Cells Q.PEAK DUO BLK ML-G10+ 400W", "qty": 30, "unit_price": 340.00, "total": 10200.00}, {"category": "Inverters", "item": "Enphase IQ8+ Microinverter", "qty": 30, "unit_price": 185.00, "total": 5550.00}, {"category": "Battery", "item": "Tesla Powerwall 3", "qty": 2, "unit_price": 11500.00, "total": 23000.00}, {"category": "Mounting", "item": "IronRidge XR10 Flush Mount System", "qty": 1, "unit_price": 2200.00, "total": 2200.00}, {"category": "Electrical", "item": "Electrical, Conduit, Disconnect", "qty": 1, "unit_price": 1500.00, "total": 1500.00}, {"category": "Labor", "item": "Installation Labor (2-day install)", "qty": 1, "unit_price": 4500.00, "total": 4500.00}, {"category": "Permits", "item": "Permits, Inspections, Interconnection", "qty": 1, "unit_price": 950.00, "total": 950.00}, {"category": "Project Management", "item": "Project Management & Commissioning", "qty": 1, "unit_price": 1200.00, "total": 1200.00}], "subtotal": 49100.00, "federal_tax_credit_30pct": -14730.00, "net_system_cost": 34370.00, "annual_production_estimate": "16,800 kWh", "annual_savings_estimate": 2350.00, "payback_period": "14.6 years", "warranty": "25-year panel, 25-year microinverter, 10-year battery, 5-year workmanship", "payment_schedule": {"deposit_50pct": 17185.00, "due_at_contract_signing": "Immediate", "install_40pct": 13748.00, "due_at_install_start": "Day 1 of install", "final_10pct": 3437.00, "due_at_final_inspection": "Within 7 days of PTO"}, "square_payment_link": "https://square.link/pay/quote-0567", "terms": "50% deposit via Square or ACH to lock equipment. 40% at install start. 10% at PTO. All major credit cards accepted (3% fee).", "notes": "Includes SolarEdge monitoring portal setup, Enphase Enlighten app configuration, and 1-year maintenance plan. Production guarantee: 15,500 kWh/year minimum."}}
```

## Example 4: Create an invoice for project milestone payment via Square

### Input

Customer: Lisa Williams, Job: JOB-2024-0423, Project: 7.2kW residential + Tesla Powerwall 2, Contract total: $28,500, Previous payments: $14,250 (50% deposit at signing), Current milestone: Installation complete June 12, Next payment due: 40% at install = $11,400, Invoice type: Progress billing, Square payment enabled

### Output

```json
{
  "action": "create_invoice",
  "invoice_id": "INV-2024-0892",
  "date": "2024-06-14",
  "due_date": "2024-06-21",
  "customer": "Lisa Williams",
  "job_id": "JOB-2024-0423",
  "project": "7.2kW Residential Solar + Tesla Powerwall 2",
  "contract_total": 28500.0,
  "previous_payments": 14250.0,
  "current_invoice_amount": 11400.0,
  "balance_remaining": 2850.0,
  "invoice_type": "Progress Billing - Installation Complete",
  "line_items": [
    {
      "description": "Installation milestone payment (40% of contract)",
      "amount": 11400.0
    }
  ],
  "payment_methods": [
    {
      "method": "Square Online Payment",
      "link": "https://square.link/pay/inv-0892",
      "fee": "No fee for ACH, 2.9% + $0.30 for cards"
    },
    {
      "method": "ACH Transfer",
      "details": "Routing: 061000104, Account ending 4521, Eko Solar LLC"
    },
    {
      "method": "Check",
      "details": "Payable to: Eko Solar LLC, Mail to: 123 Solar Way, Atlanta GA 30309"
    }
  ],
  "square_invoice_status": "Sent",
  "email_sent": true,
  "google_drive_attachment": "Invoice_PDF_INV-0892.pdf",
  "reminder_schedule": [
    "3 days before due",
    "1 day after overdue"
  ],
  "notes": "Thank you for choosing Eko Solar! Your system is installed and awaiting utility inspection. PTO expected within 5-7 business days. Final payment of $2,850 due at PTO."
}
```

## Example 5: Schedule a site survey and sync to Google Calendar

### Input

Customer: Robert Kim, Lead ID: ES-2024-0895, Address: 892 Cascade Rd SW, Atlanta GA 30311, Preferred days: Tuesday or Thursday, Preferred time: Morning (9am-12pm), Purpose: Site survey for 10kW system sizing, Roof access needed, Contact: 404-555-0147

### Output

```json
{
  "action": "schedule_appointment",
  "appointment_id": "APT-2024-0563",
  "customer": "Robert Kim",
  "lead_id": "ES-2024-0895",
  "type": "Site Survey",
  "proposed_slots": [
    {
      "date": "2024-06-18",
      "time": "9:00 AM - 11:00 AM",
      "day": "Tuesday",
      "google_calendar_event_id": "pending"
    },
    {
      "date": "2024-06-20",
      "time": "10:00 AM - 12:00 PM",
      "day": "Thursday",
      "google_calendar_event_id": "pending"
    },
    {
      "date": "2024-06-25",
      "time": "9:30 AM - 11:30 AM",
      "day": "Tuesday",
      "google_calendar_event_id": "pending"
    }
  ],
  "location": "892 Cascade Rd SW, Atlanta GA 30311",
  "duration_minutes": 90,
  "agenda": [
    "Measure roof dimensions and pitch",
    "Assess shading from trees/structures",
    "Check electrical panel capacity",
    "Identify conduit routing",
    "Discuss system goals and budget",
    "Take photos for design team"
  ],
  "prep_needed": [
    "Roof ladder and safety gear",
    "Tablet with survey app",
    "Measuring tools",
    "Sample panel photos",
    "Preliminary design template"
  ],
  "google_calendar_sync": true,
  "confirmation_email": {
    "to": "robert.k@email.com",
    "subject": "Site Survey Scheduled - Eko Solar",
    "body": "Hi Robert, your site survey is scheduled for [DATE] at [TIME]. Our technician will arrive at 892 Cascade Rd SW. Please ensure roof access is available. We'll text 30 minutes before arrival. Questions? Reply to this email or call (404) 555-SOLAR."
  },
  "reminder": {
    "sms_24h": true,
    "sms_30min": true,
    "email_24h": true
  },
  "follow_up_action": "Send preliminary design within 48 hours of survey"
}
```

## Example 6: Draft a professional follow-up email after sending a quote

### Input

Customer: Jennifer Lopez, Quote ID: QTE-2024-0521, System: 8.5kW + 1 Powerwall, Quote amount: $24,800 net after tax credit, Quote sent: May 28, Last contact: June 5 (left voicemail), Days since quote: 17, Status: No response, Interest level: High during initial call

### Output

```json
{
  "action": "draft_email",
  "channel": "Email",
  "from": "Eko Solar <sales@ekosolar.com>",
  "to": "jennifer.lopez@email.com",
  "subject": "Re: Your Solar Quote - 8.5kW System ($24,800 net) - Questions?",
  "body": "Hi Jennifer,\n\nI wanted to follow up on the solar quote I sent on May 28 for your 8.5kW system with Tesla Powerwall battery backup. The net cost after the 30% federal tax credit is $24,800.\n\nI know this is a significant decision, and I'm here to help with any questions \u2014 no pressure at all. A few things that might help:\n\n- Our financing partner is offering 2.99% APR on solar loans, which could make your monthly payment around $165 (likely less than your current electric bill)\n- We have 2 installation slots open in July if you'd like to get installed before peak summer rates hit\n- I'm happy to do a quick 10-minute call to walk through any part of the quote that's unclear\n\nWould Thursday at 6pm work for a brief call? Or just reply with any questions \u2014 I'm here to help.\n\nBest regards,\n[Your name]\nEko Solar LLC\n(404) 555-SOLAR\nsales@ekosolar.com\nwww.ekosolar.com\n"
}
```

## Example 7: Look up solar equipment specs from catalog

### Input

Customer asked about panel options. Need specs for: 1) REC Alpha Pure 400W, 2) Q.Cells Q.PEAK DUO BLK ML-G10+ 400W, 3) Enphase IQ8+ microinverter, 4) SolarEdge SE10000H inverter

### Output

```json
{
  "action": "equipment_lookup",
  "results": [
    {
      "category": "Solar Panels",
      "brand": "REC",
      "model": "Alpha Pure 400W",
      "watts": 400,
      "efficiency": "22.2%",
      "warranty": "25-year product, 25-year performance (92% at year 25)",
      "dimensions": "1722 x 1134 x 30mm",
      "weight": "21.5kg",
      "temp_coefficient": "-0.26%/C",
      "made_in": "Singapore",
      "price_per_watt": 0.96,
      "best_for": "Premium residential, high efficiency, hot climates",
      "in_stock": true
    },
    {
      "category": "Solar Panels",
      "brand": "Q.Cells",
      "model": "Q.PEAK DUO BLK ML-G10+ 400W",
      "watts": 400,
      "efficiency": "20.9%",
      "warranty": "25-year product, 25-year performance (86% at year 25)",
      "dimensions": "1722 x 1134 x 32mm",
      "weight": "22.0kg",
      "temp_coefficient": "-0.34%/C",
      "made_in": "South Korea",
      "price_per_watt": 0.85,
      "best_for": "Great value residential, strong low-light performance",
      "in_stock": true
    },
    {
      "category": "Microinverters",
      "brand": "Enphase",
      "model": "IQ8+",
      "max_output": "300W AC",
      "peak_efficiency": "97%",
      "warranty": "25 years",
      "monitoring": "Enphase Enlighten per-panel monitoring",
      "price_each": 185.0,
      "best_for": "Shaded roofs, complex layouts, panel-level optimization",
      "in_stock": true
    },
    {
      "category": "String Inverters",
      "brand": "SolarEdge",
      "model": "SE10000H",
      "max_dc_input": "15000W",
      "max_ac_output": "10000W",
      "efficiency": "99.2%",
      "warranty": "12 years standard, 25-year extended available",
      "monitoring": "SolarEdge monitoring portal",
      "price": 2200.0,
      "best_for": "Large systems, battery-ready, DC optimizers for shade management",
      "in_stock": true
    }
  ],
  "summary": "REC Alpha Pure is premium at $0.96/W with highest efficiency (22.2%). Q.Cells is great value at $0.85/W with excellent low-light performance. For inverters: Enphase IQ8+ gives panel-level optimization and monitoring, ideal for shaded/complex roofs. SolarEdge SE10000H is best for large systems with battery integration and DC optimizer technology."
}
```

## Example 8: Calculate solar system sizing and annual production for Atlanta customer

### Input

Monthly electric bill: $175, Rate per kWh: $0.12, Location: Atlanta GA, Roof: South-facing, 30-degree pitch, No shading, Annual utility rate increase: 3%, Goal: 100% offset, Preferred panel: REC Alpha Pure 400W

### Output

```json
{
  "action": "calculate_system_size",
  "inputs": {
    "monthly_bill": 175,
    "rate_per_kwh": 0.12,
    "location": "Atlanta GA",
    "roof_orientation": "South",
    "roof_pitch": "30 degrees",
    "shading": "None",
    "annual_rate_increase": 0.03,
    "offset_goal": "100%",
    "panel_choice": "REC Alpha Pure 400W"
  },
  "monthly_usage_kwh": 1458,
  "annual_usage_kwh": 17500,
  "production_factor_atlanta": 4.8,
  "derate_factor": 0.85,
  "required_system_size_kw": 4.29,
  "recommended_system_size": "4.8-5.2 kW",
  "panel_count_400w": 13,
  "estimated_annual_production": "18,400 kWh",
  "first_year_savings": 2100,
  "25_year_savings": 73500,
  "payback_period_years": 9.2,
  "environmental_impact": "15.3 tons CO2 offset annually (equivalent to 340 trees)",
  "notes": "System slightly oversized to account for ~0.5%/year panel degradation. 13x REC Alpha Pure 400W = 5.2kW system. With 22.2% efficiency, these panels maximize production on limited roof space. Actual production varies +/- 10% based on weather. System includes monitoring via SolarEdge or Enphase app.",
  "incentives_applied": {
    "federal_itc_30pct": "Applied to total system cost",
    "georgia_state": "None currently - check for updates",
    "utility_rebates": "Contact Georgia Power for net metering details"
  }
}
```

## Example 9: Generate a weekly business operations report

### Input

Week: June 3-9, 2024, New leads: 14 (8 website, 4 referral, 2 walk-in), Site surveys: 6 completed, Quotes sent: 5, Quotes accepted: 2 ($47,200 total), Installations scheduled: 3, Installations completed: 2, Revenue: $47,200, Active pipeline: $156,000, Top closer: Marcus (3 deals, $71,500), Issues: Dekalb County permit delay affecting 2 projects

### Output

```json
{
  "action": "generate_report",
  "report_type": "Weekly Operations Summary",
  "period": "June 3-9, 2024",
  "platform": "Eko Solar Ops",
  "highlights": [
    {
      "metric": "New Leads",
      "value": 14,
      "breakdown": {
        "website": 8,
        "referral": 4,
        "walk_in": 2
      },
      "trend": "+3 vs last week",
      "status": "positive"
    },
    {
      "metric": "Site Surveys",
      "value": 6,
      "trend": "On target (6/week goal)",
      "status": "neutral"
    },
    {
      "metric": "Quote Acceptance Rate",
      "value": "40%",
      "trend": "+5% vs rolling 4-week avg",
      "status": "positive"
    },
    {
      "metric": "Closed Revenue",
      "value": "$47,200",
      "trend": "+12% vs weekly target ($42,000)",
      "status": "positive"
    },
    {
      "metric": "Pipeline Value",
      "value": "$156,000",
      "trend": "Stable",
      "status": "neutral"
    }
  ],
  "team_performance": [
    {
      "name": "Marcus",
      "role": "Sales Lead",
      "deals_closed": 3,
      "revenue": 71500,
      "avg_deal_size": 23833,
      "win_rate": "60%"
    }
  ],
  "pipeline_status": {
    "lead_stage": 8,
    "survey_scheduled": 4,
    "quoted": 5,
    "accepted": 2,
    "install_scheduled": 3,
    "installing": 1,
    "completed": 2,
    "invoiced": 2,
    "paid": 1
  },
  "operations": {
    "installations_completed": 2,
    "avg_install_time_days": 2.5,
    "permits_pending": 4,
    "equipment_orders": 3,
    "subcontractor_assignments": 2
  },
  "issues": [
    {
      "issue": "Dekalb County permitting delay",
      "impact": "2 projects delayed 1-2 weeks beyond target",
      "action_taken": "Contacted county rep, expedite request filed June 10",
      "escalation_needed": false,
      "expected_resolution": "June 20"
    }
  ],
  "next_week_priorities": [
    "Follow up on 3 pending quotes (response needed by June 16)",
    "Schedule 4 site surveys for new leads",
    "Push Dekalb permit expedite - follow up June 17",
    "Team meeting Monday 9am: Q2 target review (current: 68% of goal)",
    "Update equipment catalog pricing for Q3"
  ],
  "google_calendar_events": [
    "Team meeting: Mon 9:00 AM",
    "Permit follow-up: Tue 10:00 AM",
    "Survey scheduling block: Wed-Thu mornings"
  ],
  "square_reconciliation": "$14,250 deposited, $11,400 pending (2 invoices sent)",
  "summary": "Strong week with $47,200 in closed revenue beating target by 12%. Lead flow healthy at 14 new inquiries. Quote acceptance improved to 40%. Main concern is Dekalb permitting bottleneck. Action plan filed. Q2 at 68% of target with 3 weeks remaining."
}
```

## Example 10: Research permit office for solar installation

### Input

Address: 2450 Peachtree Rd NE, Atlanta GA 30305, County: Fulton, City: Atlanta, Job type: Residential solar + battery, System size: 8kW

### Output

```json
{
  "action": "permit_research",
  "address": "2450 Peachtree Rd NE, Atlanta GA 30305",
  "county": "Fulton",
  "city": "Atlanta",
  "permit_office": {
    "name": "City of Atlanta Office of Buildings",
    "address": "55 Trinity Ave SW, Atlanta GA 30303",
    "phone": "(404) 330-6180",
    "hours": "Mon-Fri 8:30 AM - 4:30 PM",
    "online_portal": "https://aca.accela.com/atlanta/Cap/CapHome.aspx"
  },
  "required_permits": [
    {
      "type": "Electrical Permit",
      "authority": "City of Atlanta",
      "estimated_cost": 150.0,
      "typical_timeline": "5-7 business days",
      "required_docs": [
        "Single-line electrical diagram",
        "Panel schedule",
        "Site plan showing equipment locations"
      ]
    },
    {
      "type": "Building Permit",
      "authority": "City of Atlanta",
      "estimated_cost": 200.0,
      "typical_timeline": "7-10 business days",
      "required_docs": [
        "Structural engineering letter (if roof load > 5 psf)",
        "Attachment method detail",
        "Manufacturer cut sheets"
      ]
    },
    {
      "type": "Interconnection Agreement",
      "authority": "Georgia Power",
      "estimated_cost": 0.0,
      "typical_timeline": "10-15 business days",
      "required_docs": [
        "Interconnection application",
        "Proof of insurance ($1M general liability)",
        "System design and spec sheet"
      ]
    }
  ],
  "total_permit_cost_estimate": 350.0,
  "total_timeline_estimate": "15-20 business days",
  "notes": "Fulton County does not require a separate county permit for residential solar - city permit only. HOA approval may be required for Peachtree Rd area - verify with property management. Georgia Power net metering available. No battery-specific permit required in Atlanta - battery treated as part of electrical permit. Expedited review available for $150 additional fee (reduces timeline to 3-5 days).",
  "next_actions": [
    "Submit electrical permit online via Atlanta portal",
    "Upload structural letter from licensed engineer",
    "Submit Georgia Power interconnection application simultaneously",
    "Schedule pre-install inspection if required"
  ]
}
```

## Example 11: Create a digital contract with e-signature for solar project

### Input

Customer: Amanda Foster, Job: JOB-2024-0156, System: 10kW + 2 Powerwalls, Contract value: $38,500, Deposit: $19,250, Payment terms: 50/40/10, Equipment: REC Alpha Pure 400W x25, SolarEdge SE10000H, Tesla Powerwall 3 x2, Timeline: Install starts July 22, PTO target: August 15

### Output

```json
{
  "action": "create_contract",
  "contract_id": "CTR-2024-0156",
  "customer": "Amanda Foster",
  "job_id": "JOB-2024-0156",
  "date": "2024-06-14",
  "system_details": {
    "size": "10kW DC",
    "panels": "REC Alpha Pure 400W (25 units)",
    "inverter": "SolarEdge SE10000H with P700 DC Optimizers",
    "battery": "Tesla Powerwall 3 (2 units)",
    "monitoring": "SolarEdge monitoring portal + Tesla app"
  },
  "contract_value": 38500.0,
  "payment_schedule": {
    "deposit_50pct": {
      "amount": 19250.0,
      "due": "Upon contract execution",
      "method": "Square, ACH, or check"
    },
    "installation_40pct": {
      "amount": 15400.0,
      "due": "Day 1 of installation",
      "method": "Square, ACH, or check"
    },
    "final_10pct": {
      "amount": 3850.0,
      "due": "Within 7 days of PTO",
      "method": "Square, ACH, or check"
    }
  },
  "work_scope": [
    "Site survey and shade analysis",
    "Custom system design and engineering",
    "All equipment procurement and delivery",
    "Permit application and utility interconnection",
    "Professional installation by licensed electricians",
    "System commissioning and monitoring setup",
    "Utility inspection coordination",
    "Permission to operate facilitation",
    "Customer training on monitoring apps",
    "1-year maintenance plan"
  ],
  "warranties": {
    "panels": "25-year product and performance warranty",
    "inverter": "12-year standard, 25-year extended available",
    "battery": "10-year warranty, 70% capacity retention",
    "workmanship": "5-year installation warranty",
    "roof_penetrations": "10-year leak-free guarantee"
  },
  "production_guarantee": "Minimum 13,500 kWh in year 1. If system underperforms by >10%, we will add panels at no cost or refund proportional difference.",
  "cancellation_terms": "Customer may cancel within 3 days of signing for full deposit refund. After 3 days, deposit is non-refundable but may be applied to future project within 12 months.",
  "e_signature": {
    "platform": "Eko Solar Ops integrated e-signature",
    "signer_email": "amanda.foster@email.com",
    "sent_date": "2024-06-14",
    "reminder_schedule": [
      "24 hours",
      "72 hours"
    ],
    "expiration": "2024-06-21"
  },
  "google_drive_storage": "Contract_CTR-2024-0156_signed.pdf",
  "notes": "Customer requested battery backup for whole-home power during outages. Tesla Powerwall 3 provides 13.5kWh each = 27kWh total backup capacity. HOA approval obtained June 10. Customer will receive real-time project updates via client portal."
}
```

## Example 12: Draft a customer onboarding welcome message

### Input

Customer: Tom Bradley, Contract signed: June 12, System: 6.5kW + 1 Powerwall, Project ID: JOB-2024-0489, Assigned project manager: Marcus, Expected install: July 8-12, Customer portal access: Enabled

### Output

```json
{
  "action": "draft_welcome_message",
  "channel": "Email",
  "from": "Eko Solar <welcome@ekosolar.com>",
  "to": "tom.bradley@email.com",
  "subject": "Welcome to Eko Solar! Your Project is Now Active (JOB-2024-0489)",
  "body": "Hi Tom,\n\nWelcome to the Eko Solar family! We're excited to get your 6.5kW solar system + Tesla Powerwall installed and saving you money.\n\nYOUR PROJECT DETAILS:\n- Project ID: JOB-2024-0489\n- System: 6.5kW (17x REC Alpha Pure 400W panels) + Tesla Powerwall 3\n- Estimated Annual Production: 10,800 kWh\n- Estimated Annual Savings: $1,450\n- Your Project Manager: Marcus\n- Direct Line: (404) 555-SOLAR ext. 3\n\nWHAT HAPPENS NEXT:\n1. Site Survey - We'll visit your home to finalize measurements (scheduled within 5 business days)\n2. Design Approval - You'll receive final system design for approval via email\n3. Permits - We handle all city and utility paperwork\n4. Equipment Order - Panels, inverter, and battery ordered (4-6 week lead time)\n5. Installation - Targeting July 8-12 (weather permitting)\n6. Inspection & PTO - Utility inspection and permission to operate\n\nYOUR CLIENT PORTAL:\nAccess your project dashboard anytime at: https://ops.lock28.com/client-portal\nLogin with: tom.bradley@email.com\n\nYou'll see real-time updates, invoices, documents, and can message our team directly.\n\nQuestions? Reply to this email or call Marcus directly.\n\nThanks for choosing solar!\n\nThe Eko Solar Team\nwww.ekosolar.com | (404) 555-SOLAR"
}
```
