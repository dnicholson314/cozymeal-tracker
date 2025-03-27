# Cozymeal Tracker - TODO List

## Testing Plan

This document outlines the tests that need to be implemented for each module in the Cozymeal Tracker application.

### app.py (Flask Application)

#### Existing Tests

- ✅ `test_home_page`: Verify home page renders correctly
- ✅ `test_post_without_auth`: Test POST request without auth header
- ✅ `test_post_with_invalid_auth`: Test POST request with incorrect auth token
- ✅ `test_post_with_valid_auth`: Test POST request with valid auth
- ✅ `test_post_with_valid_auth_no_articles`: Test POST with valid auth when no articles found

#### Additional Tests Needed

- ✅ `test_post_with_malformed_auth_header`: Test with malformed Authorization header
- ✅ `test_last_checked_updates`: Verify `last_checked` is updated after successful POST
- ✅ `test_last_checked_not_updated_on_failure`: Verify `last_checked` isn't updated on failed requests
- ✅ `test_last_checked_not_updated_on_empty`: Verify `last_checked` isn't updated when no articles (204 response)
- ✅ `test_last_checked_none`: Test behavior when `last_checked` returns None

### articles.py

#### Article Class Tests

- `test_article_initialization`: Test Article class constructor
- `test_get_pretty_title`: Test pretty title formatting (with HTML entities)
- `test_get_pretty_date_formatting`: Test date formatting in articles

#### Article Parsing Tests

- `test_get_date_published_valid_format`: Test parsing valid date formats
- `test_get_date_published_invalid_format`: Test handling invalid date formats
- `test_get_article_from_script_valid_data`: Test extracting article from valid script data
- `test_get_article_from_script_missing_fields`: Test handling missing fields in script data
- `test_get_article_from_script_malformed_data`: Test handling malformed script data

#### Archive Page Tests

- `test_get_articles_from_archive_page_success`: Test successful archive page parsing
- `test_get_articles_from_archive_page_404`: Test handling 404 response
- `test_get_articles_from_archive_page_network_error`: Test handling network errors
- `test_get_articles_from_archive_page_empty_response`: Test handling empty responses

#### Article Filtering Tests

- `test_get_new_articles_with_recent_articles`: Test filtering with recent articles
- `test_get_new_articles_with_old_articles`: Test filtering with only old articles
- `test_get_new_articles_empty_list`: Test filtering with empty article list
- `test_get_new_articles_sorting_order`: Test article sorting in results

### utils.py

#### Date Handling Tests

- `test_get_date_a_week_ago_timezone`: Test timezone handling in week-ago date calculation
- `test_get_date_a_week_before_timestamp`: Test calculating a week before a given timestamp

#### Last Checked File Tests

- `test_set_last_checked_new_file`: Test setting last_checked in new file
- `test_set_last_checked_existing_file`: Test updating existing last_checked file
- `test_set_last_checked_permission_error`: Test handling permission errors
- `test_get_last_checked_valid_file`: Test reading from valid last_checked file
- `test_get_last_checked_missing_file`: Test handling missing last_checked file
- `test_get_last_checked_corrupted_json`: Test handling corrupted JSON in file
- `test_get_last_checked_missing_key`: Test handling missing keys in last_checked data

#### Token Verification Tests

- `test_verify_token_valid_bearer`: Test verifying valid bearer token
- `test_verify_token_invalid_bearer`: Test rejecting invalid bearer token
- `test_verify_token_missing_header`: Test handling missing Authorization header
- `test_verify_token_malformed_header`: Test handling malformed Authorization header
- `test_verify_token_empty_configured_token`: Test behavior with empty configured token

### emails.py

#### Email Formatting Tests

- `test_format_articles_for_email_single_article`: Test formatting single article for email
- `test_format_articles_for_email_multiple_articles`: Test formatting multiple articles
- `test_format_articles_for_email_empty_list`: Test formatting empty article list
- `test_format_articles_for_email_special_characters`: Test handling special characters

#### Message Creation Tests

- `test_get_message_for_email_headers`: Test email headers in created message
- `test_get_message_for_email_content_type`: Test content type in email
- `test_get_message_for_email_multipart`: Test multipart email structure
- `test_get_message_for_email_attachments`: Test email attachments if applicable

#### Email Sending Tests

- `test_send_email_for_articles_success`: Test successful email sending
- `test_send_email_for_articles_smtp_error`: Test handling SMTP errors
- `test_send_email_for_articles_auth_error`: Test handling authentication errors
- `test_send_email_for_articles_network_error`: Test handling network errors

### settings.py

#### Environment Variable Tests

- `test_required_env_vars_present`: Test that required env vars are loaded
- `test_optional_env_vars_defaults`: Test default values for optional env vars
- `test_invalid_env_vars`: Test handling of invalid environment variables

#### Path Handling Tests

- `test_last_checked_dir_creation`: Test creation of last_checked directory
- `test_last_checked_dir_permissions`: Test directory permissions handling

#### Timezone Tests

- `test_default_timezone_validity`: Test validity of default timezone setting

## Testing Implementation Notes

1. Use mocking for external services (SMTP, HTTP requests)
2. Create fixtures for common test data
3. Use parameterized tests for different input scenarios
4. Use temporary files/directories for file-based tests
5. Include proper cleanup in teardown methods
6. Handle timezone-sensitive tests carefully
