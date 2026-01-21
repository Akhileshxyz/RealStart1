JSON API Response.md
{
  "dashboard": {
    "header": {
      "appName": "RealStart Legal",
      "portalType": "Lawyer Portal",
      "user": {
        "name": "Adv. Sharma",
        "initials": "AD",
        "welcomeTitle": "Welcome back, Adv. Sharma",
        "subtitle": "Here's your practice overview"
      },
      "actions": {
        "viewSchedule": {
          "label": "View Schedule",
          "href": "https://realstart.pavand.in/lawyer/schedule"
        },
        "viewAllCases": {
          "label": "View All Cases",
          "href": "https://realstart.pavand.in/lawyer/cases"
        }
      }
    },
    "sidebar": {
      "brand": "RealStart Legal",
      "sections": [
        {
          "title": "Main Menu",
          "items": [
            { "label": "Dashboard", "href": "https://realstart.pavand.in/lawyer/dashboard", "active": true },
            { "label": "Cases", "href": "https://realstart.pavand.in/lawyer/cases" },
            { "label": "Clients", "href": "https://realstart.pavand.in/lawyer/clients" },
            { "label": "Schedule", "href": "https://realstart.pavand.in/lawyer/schedule" },
            { "label": "Analytics", "href": "https://realstart.pavand.in/lawyer/analytics" }
          ]
        },
        {
          "title": "Settings",
          "items": [
            { "label": "Notifications", "href": "https://realstart.pavand.in/lawyer/notifications" },
            { "label": "Settings", "href": "https://realstart.pavand.in/lawyer/settings" }
          ]
        }
      ],
      "footer": {
        "copyright": "© 2024 RealStart Legal"
      },
      "controls": {
        "toggleSidebar": true,
        "toggleTheme": true
      }
    },
    "topBar": {
      "notificationsShortcut": "alt+T",
      "notificationsLink": "https://realstart.pavand.in/lawyer/notifications"
    },
    "overviewCards": [
      {
        "id": "active_cases",
        "title": "Active Cases",
        "value": 24,
        "deltaText": "+3 this week"
      },
      {
        "id": "total_clients",
        "title": "Total Clients",
        "value": 156,
        "deltaText": "+12 this month"
      },
      {
        "id": "pending_reviews",
        "title": "Pending Reviews",
        "value": 8,
        "deltaText": "2 urgent"
      },
      {
        "id": "completed_cases",
        "title": "Completed",
        "value": 342,
        "deltaText": "98% success"
      }
    ],
    "sections": [
      {
        "id": "recent_cases",
        "title": "Recent Cases",
        "subtitle": "Latest legal consultation requests",
        "cta": {
          "label": "View All",
          "href": "https://realstart.pavand.in/lawyer/cases"
        },
        "items": [
          {
            "clientInitials": "RS",
            "clientName": "Rahul Sharma",
            "project": "Green Valley Heights",
            "serviceType": "Document Review",
            "status": "IN PROGRESS",
            "priority": {
              "level": "high",
              "label": "high priority"
            }
          },
          {
            "clientInitials": "PP",
            "clientName": "Priya Patel",
            "project": "Urban Skyline",
            "serviceType": "Title Search",
            "status": "PENDING",
            "priority": {
              "level": "medium",
              "label": "medium priority"
            }
          },
          {
            "clientInitials": "AK",
            "clientName": "Amit Kumar",
            "project": "Lake View Apartments",
            "serviceType": "Legal Consultation",
            "status": "COMPLETED",
            "priority": {
              "level": "low",
              "label": "low priority"
            }
          },
          {
            "clientInitials": "SR",
            "clientName": "Sneha Reddy",
            "project": "Metro Heights",
            "serviceType": "RERA Verification",
            "status": "IN PROGRESS",
            "priority": {
              "level": "high",
              "label": "high priority"
            }
          }
        ]
      },
      {
        "id": "todays_consultations",
        "title": "Today's Consultations",
        "date": "December 26, 2024",
        "items": [
          {
            "time": "10:00 AM",
            "clientName": "Vikram Singh",
            "project": "Prestige Tower",
            "mode": "Video Call"
          },
          {
            "time": "2:00 PM",
            "clientName": "Anjali Mehta",
            "project": "Palm Gardens",
            "mode": "In-person"
          },
          {
            "time": "4:30 PM",
            "clientName": "Rajesh Gupta",
            "project": "Sunrise Villas",
            "mode": "Phone Call"
          }
        ],
        "cta": {
          "label": "View Full Schedule",
          "href": "https://realstart.pavand.in/lawyer/schedule"
        }
      },
      {
        "id": "performance",
        "title": "Performance",
        "metrics": [
          {
            "name": "Client Satisfaction",
            "value": "4.8/5.0"
          },
          {
            "name": "Response Time",
            "value": "2.4 hrs avg"
          },
          {
            "name": "Case Success Rate",
            "value": "98%"
          }
        ]
      },
      {
        "id": "earnings",
        "title": "Earnings This Month",
        "total": "₹1,45,000",
        "deltaText": "+12% from last month",
        "breakdown": [
          {
            "category": "Document Reviews",
            "amount": "₹75,000"
          },
          {
            "category": "Consultations",
            "amount": "₹45,000"
          },
          {
            "category": "Title Searches",
            "amount": "₹25,000"
          }
        ]
      },
      {
        "id": "alerts",
        "title": "Alerts",
        "items": [
          {
            "text": "2 cases require urgent attention",
            "severity": "high"
          },
          {
            "text": "High priority document reviews pending for more than 24 hours",
            "severity": "high",
            "cta": {
              "label": "View Cases",
              "href": "https://realstart.pavand.in/lawyer/cases?priority=high"
            }
          }
        ]
      }
    ]
  }
} [realstart.pavand](https://realstart.pavand.in/lawyer/dashboard)

2. cases
{
  "casesPage": {
    "header": {
      "portalType": "Lawyer Portal",
      "appName": "RealStart Legal",
      "user": {
        "name": "Adv. Sharma",
        "initials": "AD"
      },
      "topBar": {
        "notificationsShortcut": "alt+T",
        "notificationsLink": "https://realstart.pavand.in/lawyer/notifications"
      }
    },
    "sidebar": {
      "brand": "RealStart Legal",
      "sections": [
        {
          "title": "Main Menu",
          "items": [
            {
              "label": "Dashboard",
              "href": "https://realstart.pavand.in/lawyer/dashboard",
              "active": false
            },
            {
              "label": "Cases",
              "href": "https://realstart.pavand.in/lawyer/cases",
              "active": true
            },
            {
              "label": "Clients",
              "href": "https://realstart.pavand.in/lawyer/clients",
              "active": false
            },
            {
              "label": "Schedule",
              "href": "https://realstart.pavand.in/lawyer/schedule",
              "active": false
            },
            {
              "label": "Analytics",
              "href": "https://realstart.pavand.in/lawyer/analytics",
              "active": false
            }
          ]
        },
        {
          "title": "Settings",
          "items": [
            {
              "label": "Notifications",
              "href": "https://realstart.pavand.in/lawyer/notifications"
            },
            {
              "label": "Settings",
              "href": "https://realstart.pavand.in/lawyer/settings"
            }
          ]
        }
      ],
      "footer": {
        "text": "© 2024 RealStart Legal"
      },
      "controls": {
        "toggleSidebar": true,
        "toggleTheme": true
      }
    },
    "titleSection": {
      "title": "Cases",
      "subtitle": "Manage your legal consultation cases"
    },
    "stats": [
      {
        "id": "total_cases",
        "label": "Total Cases",
        "value": 5
      },
      {
        "id": "pending_cases",
        "label": "Pending",
        "value": 2
      },
      {
        "id": "in_progress_cases",
        "label": "In Progress",
        "value": 2
      },
      {
        "id": "completed_cases",
        "label": "Completed",
        "value": 1
      }
    ],
    "filters": {
      "search": {
        "placeholder": "Search by client or property...",
        "ariaLabel": "Search by client or property..."
      },
      "status": {
        "label": "Status",
        "value": "All Status",
        "options": [
          "All Status",
          "Pending",
          "In Progress",
          "Completed"
        ]
      },
      "type": {
        "label": "Type",
        "value": "All Types",
        "options": [
          "All Types",
          "Document Review",
          "Title Search",
          "Legal Consultation",
          "RERA Verification",
          "Agreement Draft"
        ]
      }
    },
    "casesList": [
      {
        "clientInitials": "RS",
        "clientName": "Rahul Sharma",
        "serviceType": "Document Review",
        "priority": "High Priority",
        "propertyName": "Green Valley Heights",
        "location": "Pune, Maharashtra",
        "status": "In Progress",
        "date": "12/24/2024",
        "actions": {
          "viewDetails": {
            "label": "View Details"
          }
        }
      },
      {
        "clientInitials": "PP",
        "clientName": "Priya Patel",
        "serviceType": "Title Search",
        "propertyName": "Urban Skyline",
        "location": "Mumbai, Maharashtra",
        "status": "Pending",
        "date": "12/23/2024",
        "actions": {
          "viewDetails": {
            "label": "View Details"
          }
        }
      },
      {
        "clientInitials": "AK",
        "clientName": "Amit Kumar",
        "serviceType": "Legal Consultation",
        "propertyName": "Lake View Apartments",
        "location": "Bangalore, Karnataka",
        "status": "Completed",
        "date": "12/22/2024",
        "actions": {
          "viewDetails": {
            "label": "View Details"
          }
        }
      },
      {
        "clientInitials": "SR",
        "clientName": "Sneha Reddy",
        "serviceType": "RERA Verification",
        "priority": "High Priority",
        "propertyName": "Metro Heights",
        "location": "Hyderabad, Telangana",
        "status": "In Progress",
        "date": "12/21/2024",
        "actions": {
          "viewDetails": {
            "label": "View Details"
          }
        }
      },
      {
        "clientInitials": "VS",
        "clientName": "Vikram Singh",
        "serviceType": "Agreement Draft",
        "propertyName": "Prestige Tower",
        "location": "Delhi NCR",
        "status": "Pending",
        "date": "12/20/2024",
        "actions": {
          "viewDetails": {
            "label": "View Details"
          }
        }
      }
    ]
  }
}

3. clients
{
  "clientsPage": {
    "header": {
      "portalType": "Lawyer Portal",
      "appName": "RealStart Legal",
      "user": {
        "name": "Adv. Sharma",
        "initials": "AD"
      },
      "topBar": {
        "notificationsShortcut": "alt+T",
          "notificationsLink": "https://realstart.pavand.in/lawyer/notifications"
      }
    },
    "sidebar": {
      "brand": "RealStart Legal",
      "sections": [
        {
          "title": "Main Menu",
          "items": [
            {
              "label": "Dashboard",
              "href": "https://realstart.pavand.in/lawyer/dashboard",
              "active": false
            },
            {
              "label": "Cases",
              "href": "https://realstart.pavand.in/lawyer/cases",
              "active": false
            },
            {
              "label": "Clients",
              "href": "https://realstart.pavand.in/lawyer/clients",
              "active": true
            },
            {
              "label": "Schedule",
              "href": "https://realstart.pavand.in/lawyer/schedule",
              "active": false
            },
            {
              "label": "Analytics",
              "href": "https://realstart.pavand.in/lawyer/analytics",
              "active": false
            }
          ]
        },
        {
          "title": "Settings",
          "items": [
            {
              "label": "Notifications",
              "href": "https://realstart.pavand.in/lawyer/notifications"
            },
            {
              "label": "Settings",
              "href": "https://realstart.pavand.in/lawyer/settings"
            }
          ]
        }
      ],
      "footer": {
        "text": "© 2024 RealStart Legal"
      },
      "controls": {
        "toggleSidebar": true,
        "toggleTheme": true
      }
    },
    "titleSection": {
      "title": "Clients",
      "subtitle": "Manage your client relationships"
    },
    "stats": [
      {
        "id": "total_clients",
        "label": "Total Clients",
        "value": 5
      },
      {
        "id": "active_clients",
        "label": "Active Clients",
        "value": 4
      },
      {
        "id": "cases_completed",
        "label": "Cases Completed",
        "value": 17
      },
      {
        "id": "new_this_month",
        "label": "New This Month",
        "value": 0
      }
    ],
    "filters": {
      "search": {
        "placeholder": "Search by name, email, or city...",
        "ariaLabel": "Search by name, email, or city..."
      }
    },
    "clientsList": [
      {
        "clientInitials": "RS",
        "name": "Rahul Sharma",
        "email": "rahul@email.com",
        "city": "Pune",
        "stats": {
          "totalCases": 5,
          "activeCases": 2,
          "completedCases": 3
        },
        "actions": {
          "view": {
            "label": "View"
          }
        }
      },
      {
        "clientInitials": "PP",
        "name": "Priya Patel",
        "email": "priya@email.com",
        "city": "Mumbai",
        "stats": {
          "totalCases": 3,
          "activeCases": 1,
          "completedCases": 2
        },
        "actions": {
          "view": {
            "label": "View"
          }
        }
      },
      {
        "clientInitials": "AK",
        "name": "Amit Kumar",
        "email": "amit@email.com",
        "city": "Bangalore",
        "stats": {
          "totalCases": 8,
          "activeCases": 0,
          "completedCases": 8
        },
        "actions": {
          "view": {
            "label": "View"
          }
        }
      },
      {
        "clientInitials": "SR",
        "name": "Sneha Reddy",
        "email": "sneha@email.com",
        "city": "Hyderabad",
        "stats": {
          "totalCases": 2,
          "activeCases": 1,
          "completedCases": 1
        },
        "actions": {
          "view": {
            "label": "View"
          }
        }
      },
      {
        "clientInitials": "VS",
        "name": "Vikram Singh",
        "email": "vikram@email.com",
        "city": "Delhi NCR",
        "stats": {
          "totalCases": 4,
          "activeCases": 1,
          "completedCases": 3
        },
        "actions": {
          "view": {
            "label": "View"
          }
        }
      }
    ]
  }
}

4. schedule
{
  "schedulePage": {
    "header": {
      "portalType": "Lawyer Portal",
      "appName": "RealStart Legal",
      "user": {
        "name": "Adv. Sharma",
        "initials": "AD"
      },
      "topBar": {
        "notificationsShortcut": "alt+T",
        "notificationsLink": "https://realstart.pavand.in/lawyer/notifications"
      }
    },
    "sidebar": {
      "brand": "RealStart Legal",
      "sections": [
        {
          "title": "Main Menu",
          "items": [
            {
              "label": "Dashboard",
              "href": "https://realstart.pavand.in/lawyer/dashboard",
              "active": false
            },
            {
              "label": "Cases",
              "href": "https://realstart.pavand.in/lawyer/cases",
              "active": false
            },
            {
              "label": "Clients",
              "href": "https://realstart.pavand.in/lawyer/clients",
              "active": false
            },
            {
              "label": "Schedule",
              "href": "https://realstart.pavand.in/lawyer/schedule",
              "active": true
            },
            {
              "label": "Analytics",
              "href": "https://realstart.pavand.in/lawyer/analytics",
              "active": false
            }
          ]
        },
        {
          "title": "Settings",
          "items": [
            {
              "label": "Notifications",
              "href": "https://realstart.pavand.in/lawyer/notifications"
            },
            {
              "label": "Settings",
              "href": "https://realstart.pavand.in/lawyer/settings"
            }
          ]
        }
      ],
      "footer": {
        "text": "© 2024 RealStart Legal"
      },
      "controls": {
        "toggleSidebar": true,
        "toggleTheme": true
      }
    },
    "titleSection": {
      "title": "Schedule",
      "subtitle": "Manage your appointments and court dates"
    },
    "actions": {
      "addEvent": {
        "label": "Add Event"
      }
    },
    "calendar": {
      "monthTitle": "January 2026",
      "weekdays": [
        "Sun",
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat"
      ],
      "days": [
        1, 2, 3, 4, 5, 6, 7,
        8, 9, 10, 11, 12, 13, 14,
        15, 16, 17, 18, 19, 20, 21,
        22, 23, 24, 25, 26, 27, 28,
        29, 30, 31
      ]
    },
    "todaySection": {
      "title": "Today's Schedule",
      "items": [
        {
          "title": "Court Hearing - Property Dispute",
          "time": "10:00 AM",
          "location": "City Civil Court, Room 12",
          "type": "Court"
        },
        {
          "title": "Client Meeting",
          "time": "2:00 PM",
          "location": "Office",
          "type": "Meeting"
        }
      ]
    },
    "upcomingSection": {
      "title": "Upcoming",
      "items": [
        {
          "title": "Document Review",
          "date": "27 Dec",
          "time": "11:00 AM",
          "clientOrPlace": "Amit Kumar",
          "type": "Task"
        },
        {
          "title": "Court Hearing - Title Case",
          "date": "28 Dec",
          "time": "9:30 AM",
          "clientOrPlace": "Sunita Verma",
          "type": "Court"
        },
        {
          "title": "Site Visit",
          "date": "28 Dec",
          "time": "3:00 PM",
          "clientOrPlace": "Deepak Gupta",
          "type": "Site Visit"
        }
      ]
    }
  }
}


5. analytics

{
  "analyticsPage": {
    "header": {
      "portalType": "Lawyer Portal",
      "appName": "RealStart Legal",
      "user": {
        "name": "Adv. Sharma",
        "initials": "AD"
      },
      "topBar": {
        "notificationsShortcut": "alt+T",
        "notificationsLink": "https://realstart.pavand.in/lawyer/notifications"
      }
    },
    "sidebar": {
      "brand": "RealStart Legal",
      "sections": [
        {
          "title": "Main Menu",
          "items": [
            {
              "label": "Dashboard",
              "href": "https://realstart.pavand.in/lawyer/dashboard",
              "active": false
            },
            {
              "label": "Cases",
              "href": "https://realstart.pavand.in/lawyer/cases",
              "active": false
            },
            {
              "label": "Clients",
              "href": "https://realstart.pavand.in/lawyer/clients",
              "active": false
            },
            {
              "label": "Schedule",
              "href": "https://realstart.pavand.in/lawyer/schedule",
              "active": false
            },
            {
              "label": "Analytics",
              "href": "https://realstart.pavand.in/lawyer/analytics",
              "active": true
            }
          ]
        },
        {
          "title": "Settings",
          "items": [
            {
              "label": "Notifications",
              "href": "https://realstart.pavand.in/lawyer/notifications"
            },
            {
              "label": "Settings",
              "href": "https://realstart.pavand.in/lawyer/settings"
            }
          ]
        }
      ],
      "footer": {
        "text": "© 2024 RealStart Legal"
      },
      "controls": {
        "toggleSidebar": true,
        "toggleTheme": true
      }
    },
    "titleSection": {
      "title": "Analytics",
      "subtitle": "Your year-on-year performance and case statistics"
    },
    "keyMetrics": [
      {
        "id": "total_cases",
        "title": "Total Cases",
        "value": 58,
        "delta": "+12%",
        "deltaLabel": "vs last period",
        "icon": "briefcase"
      },
      {
        "id": "active_clients",
        "title": "Active Clients",
        "value": 24,
        "delta": "+8%",
        "deltaLabel": "vs last period",
        "icon": "people"
      },
      {
        "id": "total_earnings",
        "title": "Total Earnings",
        "value": "₹12.8L",
        "delta": "+18%",
        "deltaLabel": "vs last period",
        "icon": "rupee"
      },
      {
        "id": "avg_resolution_time",
        "title": "Avg Resolution Time",
        "value": "45 days",
        "delta": "-8%",
        "deltaLabel": "vs last period",
        "icon": "clock"
      }
    ],
    "charts": [
      {
        "id": "cases_earnings_trend",
        "title": "Cases & Earnings Trend",
        "type": "combo",
        "months": [
          "Jul",
          "Aug",
          "Sep",
          "Oct",
          "Nov",
          "Dec"
        ],
        "series": [
          {
            "name": "cases",
            "label": "cases",
            "data": [4, 6, 5, 8, 7, 11],
            "color": "#FF9500"
          },
          {
            "name": "earnings",
            "label": "earnings",
            "data": [120000, 140000, 130000, 210000, 180000, 280000],
            "color": "#FF9500",
            "type": "line"
          }
        ]
      },
      {
        "id": "case_type_distribution",
        "title": "Case Type Distribution",
        "type": "donut",
        "data": [
          {
            "name": "Title Verification",
            "value": 25,
            "color": "#FF9500"
          },
          {
            "name": "Property Disputes",
            "value": 20,
            "color": "#FFB84D"
          },
          {
            "name": "RERA Cases",
            "value": 30,
            "color": "#FFC966"
          },
          {
            "name": "Documentation",
            "value": 18,
            "color": "#FF9500"
          },
          {
            "name": "Other",
            "value": 7,
            "color": "#666666"
          }
        ]
      },
      {
        "id": "case_resolution",
        "title": "Case Resolution",
        "type": "bar",
        "categories": [
          "Won",
          "Lost",
          "Settled",
          "Pending"
        ],
        "data": [
          {
            "name": "Cases",
            "data": [32, 5, 15, 6]
          }
        ]
      },
      {
        "id": "client_acquisition",
        "title": "Client Acquisition",
        "type": "bar",
        "months": [
          "Jan",
          "Feb",
          "Mar",
          "Apr",
          "May",
          "Jun",
          "Jul",
          "Aug"
        ],
        "data": [
          {
            "name": "New Clients",
            "data": [3, 5, 4, 7, 6, 8, 5, 6]
          }
        ]
      }
    ]
  }
}

ii) settings
notifications
{
  "notificationsPage": {
    "header": {
      "portalType": "Lawyer Portal",
      "appName": "RealStart Legal",
      "user": {
        "name": "Adv. Sharma",
        "initials": "AD"
      },
      "topBar": {
        "notificationsShortcut": "alt+T",
        "notificationsLink": "https://realstart.pavand.in/lawyer/notifications"
      }
    },
    "sidebar": {
      "brand": "RealStart Legal",
      "sections": [
        {
          "title": "Main Menu",
          "items": [
            {
              "label": "Dashboard",
              "href": "https://realstart.pavand.in/lawyer/dashboard",
              "active": false
            },
            {
              "label": "Cases",
              "href": "https://realstart.pavand.in/lawyer/cases",
              "active": false
            },
            {
              "label": "Clients",
              "href": "https://realstart.pavand.in/lawyer/clients",
              "active": false
            },
            {
              "label": "Schedule",
              "href": "https://realstart.pavand.in/lawyer/schedule",
              "active": false
            },
            {
              "label": "Analytics",
              "href": "https://realstart.pavand.in/lawyer/analytics",
              "active": false
            }
          ]
        },
        {
          "title": "Settings",
          "items": [
            {
              "label": "Notifications",
              "href": "https://realstart.pavand.in/lawyer/notifications",
              "active": true
            },
            {
              "label": "Settings",
              "href": "https://realstart.pavand.in/lawyer/settings"
            }
          ]
        }
      ],
      "footer": {
        "text": "© 2024 RealStart Legal"
      },
      "controls": {
        "toggleSidebar": true,
        "toggleTheme": true
      }
    },
    "notificationsList": [
      {
        "id": "notification_1",
        "type": "New Client Registration",
        "icon": "user",
        "title": "New Client Registration",
        "message": "Priya Patel has registered and requested legal consultation.",
        "timestamp": "2 hours ago",
        "actions": {
          "markAsRead": {
            "icon": "checkmark"
          },
          "delete": {
            "icon": "trash"
          }
        }
      },
      {
        "id": "notification_2",
        "type": "Document Uploaded",
        "icon": "briefcase",
        "title": "Document Uploaded",
        "message": "Amit Kumar has uploaded new documents for case #LC-2024-042.",
        "timestamp": "3 hours ago",
        "actions": {
          "delete": {
            "icon": "trash"
          }
        }
      },
      {
        "id": "notification_3",
        "type": "Meeting Rescheduled",
        "icon": "calendar",
        "title": "Meeting Rescheduled",
        "message": "Your meeting with Sunita Verma has been rescheduled to Dec 28.",
        "timestamp": "5 hours ago",
        "actions": {
          "delete": {
            "icon": "trash"
          }
        }
      },
      {
        "id": "notification_4",
        "type": "Profile Update Reminder",
        "icon": "bell",
        "title": "Profile Update Reminder",
        "message": "Please update your bar council registration details.",
        "timestamp": "1 day ago",
        "actions": {
          "delete": {
            "icon": "trash"
          }
        }
      }
    ],
    "preferencesSection": {
      "title": "Notification Preferences",
      "icon": "settings",
      "preferences": [
        {
          "id": "email_notifications",
          "label": "Email Notifications",
          "description": "Receive notifications via email",
          "enabled": true,
          "toggleSwitch": true
        },
        {
          "id": "case_updates",
          "label": "Case Updates",
          "description": "Get notified about case status changes",
          "enabled": true,
          "toggleSwitch": true
        },
        {
          "id": "schedule_reminders",
          "label": "Schedule Reminders",
          "description": "Receive reminders for upcoming events",
          "enabled": true,
          "toggleSwitch": true
        },
        {
          "id": "client_requests",
          "label": "Client Requests",
          "description": "Get notified about new client inquiries",
          "enabled": true,
          "toggleSwitch": true
        }
      ]
    }
  }
}

settings

{
  "settingsPage": {
    "header": {
      "portalType": "Lawyer Portal",
      "appName": "RealStart Legal",
      "user": {
        "name": "Adv. Sharma",
        "initials": "AD"
      },
      "topBar": {
        "notificationsShortcut": "alt+T",
        "notificationsLink": "https://realstart.pavand.in/lawyer/notifications"
      }
    },
    "sidebar": {
      "brand": "RealStart Legal",
      "sections": [
        {
          "title": "Main Menu",
          "items": [
            {
              "label": "Dashboard",
              "href": "https://realstart.pavand.in/lawyer/dashboard",
              "active": false
            },
            {
              "label": "Cases",
              "href": "https://realstart.pavand.in/lawyer/cases",
              "active": false
            },
            {
              "label": "Clients",
              "href": "https://realstart.pavand.in/lawyer/clients",
              "active": false
            },
            {
              "label": "Schedule",
              "href": "https://realstart.pavand.in/lawyer/schedule",
              "active": false
            },
            {
              "label": "Analytics",
              "href": "https://realstart.pavand.in/lawyer/analytics",
              "active": false
            }
          ]
        },
        {
          "title": "Settings",
          "items": [
            {
              "label": "Notifications",
              "href": "https://realstart.pavand.in/lawyer/notifications",
              "active": false
            },
            {
              "label": "Settings",
              "href": "https://realstart.pavand.in/lawyer/settings",
              "active": true
            }
          ]
        }
      ],
      "footer": {
        "text": "© 2024 RealStart Legal"
      },
      "controls": {
        "toggleSidebar": true,
        "toggleTheme": true
      }
    },
    "titleSection": {
      "title": "Settings",
      "subtitle": "Manage your account and preferences"
    },
    "sections": [
      {
        "id": "profile_information",
        "icon": "user",
        "title": "Profile Information",
        "subtitle": "Update your personal and professional details",
        "profilePhoto": {
          "initials": "RS",
          "backgroundColor": "#FF9500",
          "action": "Change Photo",
          "fileRequirements": "JPG, PNG. Max 2MB."
        },
        "fields": [
          {
            "id": "full_name",
            "label": "Full Name",
            "type": "text",
            "value": "Adv. Rajesh Sharma",
            "placeholder": "Enter full name"
          },
          {
            "id": "email",
            "label": "Email",
            "type": "email",
            "value": "rajesh.sharma@lawfirm.com",
            "placeholder": "Enter email address"
          },
          {
            "id": "phone",
            "label": "Phone",
            "type": "tel",
            "value": "+91 9876543210",
            "placeholder": "Enter phone number"
          },
          {
            "id": "bar_council_number",
            "label": "Bar Council Number",
            "type": "text",
            "value": "KAR/1234/2015",
            "placeholder": "Enter bar council registration number"
          },
          {
            "id": "specialization",
            "label": "Specialization",
            "type": "select",
            "value": "Property Law",
            "options": [
              "Property Law",
              "Civil Law",
              "Criminal Law",
              "Corporate Law",
              "Family Law",
              "Other"
            ]
          },
          {
            "id": "experience",
            "label": "Experience",
            "type": "select",
            "value": "5-10 years",
            "options": [
              "0-2 years",
              "2-5 years",
              "5-10 years",
              "10-15 years",
              "15+ years"
            ]
          },
          {
            "id": "city",
            "label": "City",
            "type": "select",
            "value": "Bangalore",
            "options": [
              "Mumbai",
              "Delhi",
              "Bangalore",
              "Hyderabad",
              "Pune",
              "Chennai",
              "Kolkata",
              "Other"
            ]
          },
          {
            "id": "office_address",
            "label": "Office Address",
            "type": "textarea",
            "value": "123, Law Chambers, MG Road, Bangalore - 560001",
            "placeholder": "Enter office address"
          },
          {
            "id": "bio",
            "label": "Professional Bio",
            "type": "textarea",
            "value": "Experienced property lawyer with 8+ years of expertise in real estate law, title verification, and RERA compliance. Successfully handled 500+ property transactions.",
            "placeholder": "Enter professional bio"
          }
        ]
      },
      {
        "id": "availability",
        "icon": "calendar",
        "title": "Availability",
        "subtitle": "Set your working days and hours for consultations",
        "workingDays": [
          {
            "day": "Mon",
            "enabled": true
          },
          {
            "day": "Tue",
            "enabled": true
          },
          {
            "day": "Wed",
            "enabled": true
          },
          {
            "day": "Thu",
            "enabled": true
          },
          {
            "day": "Fri",
            "enabled": true
          },
          {
            "day": "Sat",
            "enabled": false
          },
          {
            "day": "Sun",
            "enabled": false
          }
        ],
        "timings": [
          {
            "id": "start_time",
            "label": "Start Time",
            "type": "time",
            "value": "09:00 AM",
            "placeholder": "Select start time"
          },
          {
            "id": "end_time",
            "label": "End Time",
            "type": "time",
            "value": "06:00 PM",
            "placeholder": "Select end time"
          }
        ]
      },
      {
        "id": "notifications_settings",
        "icon": "bell",
        "title": "Notifications",
        "subtitle": "Choose what notifications you want to receive",
        "preferences": [
          {
            "id": "new_case_assignments",
            "label": "New Case Assignments",
            "description": "Get notified when a new case is assigned",
            "enabled": true,
            "type": "toggle"
          },
          {
            "id": "case_updates",
            "label": "Case Updates",
            "description": "Updates on your active cases",
            "enabled": true,
            "type": "toggle"
          },
          {
            "id": "client_messages",
            "label": "Client Messages",
            "description": "Messages from your clients",
            "enabled": true,
            "type": "toggle"
          },
          {
            "id": "payment_alerts",
            "label": "Payment Alerts",
            "description": "Notifications about payments",
            "enabled": true,
            "type": "toggle"
          },
          {
            "id": "marketing_emails",
            "label": "Marketing Emails",
            "description": "Updates and promotions from RealStart",
            "enabled": false,
            "type": "toggle"
          }
        ]
      }
    ],
    "actions": {
      "saveChanges": {
        "label": "Save Changes",
        "icon": "checkmark"
      }
    }
  }
}
