CREATE TABLE `cities` (
  `id` uuid PRIMARY KEY,
  `name` text,
  `state` text,
  `country` text,
  `is_active` boolean,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `zones` (
  `id` uuid PRIMARY KEY,
  `city_id` uuid,
  `name` text,
  `description` text,
  `is_active` boolean,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `landmarks` (
  `id` uuid PRIMARY KEY,
  `city_id` uuid,
  `zone_id` uuid,
  `name` text,
  `latitude` decimal,
  `longitude` decimal,
  `description` text,
  `is_active` boolean,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `users` (
  `id` uuid PRIMARY KEY,
  `full_name` text,
  `email` text,
  `phone` text,
  `password_hash` text,
  `preferred_language` text,
  `is_active` boolean,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `roles` (
  `id` uuid PRIMARY KEY,
  `name` text,
  `description` text,
  `permissions` json,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `user_roles` (
  `id` uuid PRIMARY KEY,
  `user_id` uuid,
  `role_id` uuid,
  `assigned_by_user_id` uuid,
  `created_at` timestamp
);

CREATE TABLE `admins` (
  `id` uuid PRIMARY KEY,
  `user_id` uuid,
  `admin_type` text,
  `assigned_cities` json,
  `assigned_zones` json,
  `permissions` json,
  `is_active` boolean,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `lawyers` (
  `id` uuid PRIMARY KEY,
  `user_id` uuid,
  `firm_name` text,
  `bar_council_number` text,
  `years_of_experience` int,
  `specialization` text,
  `profile_photo_url` text,
  `bio` text,
  `consultation_fee` decimal,
  `sla_hours` int,
  `is_verified` boolean,
  `is_active` boolean,
  `rating` decimal,
  `total_reviews` int,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `lawyer_availability` (
  `id` uuid PRIMARY KEY,
  `lawyer_id` uuid,
  `day_of_week` int,
  `start_time` time,
  `end_time` time,
  `is_available` boolean,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `lawyer_projects` (
  `id` uuid PRIMARY KEY,
  `lawyer_id` uuid,
  `project_id` uuid,
  `assigned_by_user_id` uuid,
  `assigned_date` timestamp,
  `is_primary` boolean,
  `created_at` timestamp
);

CREATE TABLE `developers` (
  `id` uuid PRIMARY KEY,
  `name` text,
  `legal_name` text,
  `owner_name` text,
  `gst_number` text,
  `rera_number` text,
  `sub_developer` text,
  `office_address` text,
  `contact_email` text,
  `contact_phone` text,
  `logo_url` text,
  `about_text` text,
  `is_verified` boolean,
  `is_active` boolean,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `developer_users` (
  `id` uuid PRIMARY KEY,
  `developer_id` uuid,
  `user_id` uuid,
  `role_in_developer` text,
  `is_primary_contact` boolean,
  `created_at` timestamp
);

CREATE TABLE `sales_people` (
  `id` uuid PRIMARY KEY,
  `user_id` uuid,
  `developer_id` uuid,
  `designation` text,
  `is_active` boolean,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `projects` (
  `id` uuid PRIMARY KEY,
  `developer_id` uuid,
  `city_id` uuid,
  `zone_id` uuid,
  `name` text,
  `slug` text,
  `approval_type` text,
  `rera_number` text,
  `launch_year` int,
  `latitude` decimal,
  `longitude` decimal,
  `address` text,
  `status` text,
  `highlight_tag` text,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `project_details_i18n` (
  `id` uuid PRIMARY KEY,
  `project_id` uuid,
  `language` text,
  `short_description` text,
  `long_description` text,
  `location_highlights` text,
  `amenities_text` text
);

CREATE TABLE `plots` (
  `id` uuid PRIMARY KEY,
  `project_id` uuid,
  `plot_number` text,
  `size_label` text,
  `area_sqft` decimal,
  `facing` text,
  `status` text,
  `is_corner` boolean,
  `is_park_facing` boolean,
  `is_road_facing` boolean,
  `latitude` decimal,
  `longitude` decimal,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `plot_pricing` (
  `id` uuid PRIMARY KEY,
  `plot_id` uuid,
  `rate_per_sqft` decimal,
  `base_price` decimal,
  `all_inclusive_price` decimal,
  `currency` text,
  `effective_from` timestamp,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `plot_price_history` (
  `id` uuid PRIMARY KEY,
  `plot_id` uuid,
  `old_rate_per_sqft` decimal,
  `new_rate_per_sqft` decimal,
  `changed_by_user_id` uuid,
  `changed_at` timestamp,
  `reason` text
);

CREATE TABLE `price_alerts` (
  `id` uuid PRIMARY KEY,
  `user_id` uuid,
  `city_id` uuid,
  `zone_id` uuid,
  `min_rate_per_sqft` decimal,
  `max_rate_per_sqft` decimal,
  `alert_type` text,
  `frequency` text,
  `is_active` boolean,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `document_sets` (
  `id` uuid PRIMARY KEY,
  `project_id` uuid,
  `version_number` int,
  `status` text,
  `submitted_by_user_id` uuid,
  `reviewed_by_lawyer_id` uuid,
  `review_notes` text,
  `review_summary` text,
  `reviewed_at` timestamp,
  `verification_certificate_url` text,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `document_files` (
  `id` uuid PRIMARY KEY,
  `document_set_id` uuid,
  `doc_type` text,
  `name` text,
  `file_url` text,
  `pages_count` int,
  `mime_type` text,
  `status` text,
  `status_notes` text,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `legal_call_requests` (
  `id` uuid PRIMARY KEY,
  `user_id` uuid,
  `project_id` uuid,
  `plot_id` uuid,
  `document_set_id` uuid,
  `topics` json,
  `preferred_date` date,
  `preferred_time_window` text,
  `preferred_language` text,
  `user_notes` text,
  `assigned_lawyer_id` uuid,
  `sla_hours` int,
  `status` text,
  `priority` text,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `legal_call_logs` (
  `id` uuid PRIMARY KEY,
  `legal_call_request_id` uuid,
  `lawyer_id` uuid,
  `call_summary` text,
  `recommendation` text,
  `opinion_file_url` text,
  `call_started_at` timestamp,
  `call_ended_at` timestamp,
  `call_duration_minutes` int,
  `user_satisfaction_rating` int,
  `user_feedback` text,
  `created_at` timestamp
);

CREATE TABLE `visit_bookings` (
  `id` uuid PRIMARY KEY,
  `booking_code` text,
  `user_id` uuid,
  `project_id` uuid,
  `plot_id` uuid,
  `visit_date` date,
  `visit_start_time` time,
  `visit_end_time` time,
  `preferred_language` text,
  `assigned_sales_person_id` uuid,
  `status` text,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `visit_participants` (
  `id` uuid PRIMARY KEY,
  `visit_booking_id` uuid,
  `name` text,
  `phone` text,
  `is_primary` boolean
);

CREATE TABLE `payments` (
  `id` uuid PRIMARY KEY,
  `user_id` uuid,
  `project_id` uuid,
  `plot_id` uuid,
  `legal_call_request_id` uuid,
  `visit_booking_id` uuid,
  `amount` decimal,
  `currency` text,
  `payment_gateway` text,
  `gateway_payment_id` text,
  `status` text,
  `purpose` text,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `activity_logs` (
  `id` uuid PRIMARY KEY,
  `user_id` uuid,
  `action` text,
  `entity_type` text,
  `entity_id` uuid,
  `old_values` json,
  `new_values` json,
  `ip_address` text,
  `user_agent` text,
  `created_at` timestamp
);

CREATE TABLE `system_settings` (
  `id` uuid PRIMARY KEY,
  `setting_key` text UNIQUE,
  `setting_value` json,
  `setting_type` text,
  `description` text,
  `updated_by_user_id` uuid,
  `updated_at` timestamp
);

CREATE TABLE `campaigns` (
  `id` uuid PRIMARY KEY,
  `name` text,
  `campaign_type` text,
  `city_id` uuid,
  `zone_id` uuid,
  `project_id` uuid,
  `target_audience` json,
  `message_template` text,
  `discount_percentage` decimal,
  `start_date` timestamp,
  `end_date` timestamp,
  `status` text,
  `created_by_user_id` uuid,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `analytics_events` (
  `id` uuid PRIMARY KEY,
  `user_id` uuid,
  `event_type` text,
  `event_data` json,
  `project_id` uuid,
  `plot_id` uuid,
  `session_id` text,
  `device_type` text,
  `created_at` timestamp
);

CREATE TABLE `notifications` (
  `id` uuid PRIMARY KEY,
  `user_id` uuid,
  `channel` text,
  `title` text,
  `body` text,
  `data` json,
  `status` text,
  `sent_at` timestamp,
  `read_at` timestamp,
  `created_at` timestamp
);

CREATE TABLE `qr_codes` (
  `id` uuid PRIMARY KEY,
  `project_id` uuid,
  `plot_id` uuid,
  `qr_identifier` text,
  `qr_image_url` text,
  `target_url` text,
  `created_at` timestamp
);

ALTER TABLE `zones` ADD FOREIGN KEY (`city_id`) REFERENCES `cities` (`id`);

ALTER TABLE `landmarks` ADD FOREIGN KEY (`city_id`) REFERENCES `cities` (`id`);

ALTER TABLE `landmarks` ADD FOREIGN KEY (`zone_id`) REFERENCES `zones` (`id`);

ALTER TABLE `user_roles` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `user_roles` ADD FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`);

ALTER TABLE `user_roles` ADD FOREIGN KEY (`assigned_by_user_id`) REFERENCES `users` (`id`);

ALTER TABLE `admins` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `lawyers` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `lawyer_availability` ADD FOREIGN KEY (`lawyer_id`) REFERENCES `lawyers` (`id`);

ALTER TABLE `lawyer_projects` ADD FOREIGN KEY (`lawyer_id`) REFERENCES `lawyers` (`id`);

ALTER TABLE `lawyer_projects` ADD FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`);

ALTER TABLE `lawyer_projects` ADD FOREIGN KEY (`assigned_by_user_id`) REFERENCES `users` (`id`);

ALTER TABLE `developer_users` ADD FOREIGN KEY (`developer_id`) REFERENCES `developers` (`id`);

ALTER TABLE `developer_users` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `sales_people` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `sales_people` ADD FOREIGN KEY (`developer_id`) REFERENCES `developers` (`id`);

ALTER TABLE `projects` ADD FOREIGN KEY (`developer_id`) REFERENCES `developers` (`id`);

ALTER TABLE `projects` ADD FOREIGN KEY (`city_id`) REFERENCES `cities` (`id`);

ALTER TABLE `projects` ADD FOREIGN KEY (`zone_id`) REFERENCES `zones` (`id`);

ALTER TABLE `project_details_i18n` ADD FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`);

ALTER TABLE `plots` ADD FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`);

ALTER TABLE `plot_pricing` ADD FOREIGN KEY (`plot_id`) REFERENCES `plots` (`id`);

ALTER TABLE `plot_price_history` ADD FOREIGN KEY (`plot_id`) REFERENCES `plots` (`id`);

ALTER TABLE `plot_price_history` ADD FOREIGN KEY (`changed_by_user_id`) REFERENCES `users` (`id`);

ALTER TABLE `price_alerts` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `price_alerts` ADD FOREIGN KEY (`city_id`) REFERENCES `cities` (`id`);

ALTER TABLE `price_alerts` ADD FOREIGN KEY (`zone_id`) REFERENCES `zones` (`id`);

ALTER TABLE `document_sets` ADD FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`);

ALTER TABLE `document_sets` ADD FOREIGN KEY (`submitted_by_user_id`) REFERENCES `users` (`id`);

ALTER TABLE `document_sets` ADD FOREIGN KEY (`reviewed_by_lawyer_id`) REFERENCES `lawyers` (`id`);

ALTER TABLE `document_files` ADD FOREIGN KEY (`document_set_id`) REFERENCES `document_sets` (`id`);

ALTER TABLE `legal_call_requests` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `legal_call_requests` ADD FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`);

ALTER TABLE `legal_call_requests` ADD FOREIGN KEY (`plot_id`) REFERENCES `plots` (`id`);

ALTER TABLE `legal_call_requests` ADD FOREIGN KEY (`document_set_id`) REFERENCES `document_sets` (`id`);

ALTER TABLE `legal_call_requests` ADD FOREIGN KEY (`assigned_lawyer_id`) REFERENCES `lawyers` (`id`);

ALTER TABLE `legal_call_logs` ADD FOREIGN KEY (`legal_call_request_id`) REFERENCES `legal_call_requests` (`id`);

ALTER TABLE `legal_call_logs` ADD FOREIGN KEY (`lawyer_id`) REFERENCES `lawyers` (`id`);

ALTER TABLE `visit_bookings` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `visit_bookings` ADD FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`);

ALTER TABLE `visit_bookings` ADD FOREIGN KEY (`plot_id`) REFERENCES `plots` (`id`);

ALTER TABLE `visit_bookings` ADD FOREIGN KEY (`assigned_sales_person_id`) REFERENCES `sales_people` (`id`);

ALTER TABLE `visit_participants` ADD FOREIGN KEY (`visit_booking_id`) REFERENCES `visit_bookings` (`id`);

ALTER TABLE `payments` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `payments` ADD FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`);

ALTER TABLE `payments` ADD FOREIGN KEY (`plot_id`) REFERENCES `plots` (`id`);

ALTER TABLE `payments` ADD FOREIGN KEY (`legal_call_request_id`) REFERENCES `legal_call_requests` (`id`);

ALTER TABLE `payments` ADD FOREIGN KEY (`visit_booking_id`) REFERENCES `visit_bookings` (`id`);

ALTER TABLE `activity_logs` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `system_settings` ADD FOREIGN KEY (`updated_by_user_id`) REFERENCES `users` (`id`);

ALTER TABLE `campaigns` ADD FOREIGN KEY (`city_id`) REFERENCES `cities` (`id`);

ALTER TABLE `campaigns` ADD FOREIGN KEY (`zone_id`) REFERENCES `zones` (`id`);

ALTER TABLE `campaigns` ADD FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`);

ALTER TABLE `campaigns` ADD FOREIGN KEY (`created_by_user_id`) REFERENCES `users` (`id`);

ALTER TABLE `analytics_events` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `analytics_events` ADD FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`);

ALTER TABLE `analytics_events` ADD FOREIGN KEY (`plot_id`) REFERENCES `plots` (`id`);

ALTER TABLE `notifications` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `qr_codes` ADD FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`);

ALTER TABLE `qr_codes` ADD FOREIGN KEY (`plot_id`) REFERENCES `plots` (`id`);
