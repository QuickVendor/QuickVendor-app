# 🧪 User Complaint System - Testing Guide

## 🎯 Testing Objectives
Verify the complete user complaint system integration with Sentry and Slack notifications.

## 📋 Pre-Testing Checklist
- [x] HelpModal.tsx exists with Sentry integration
- [x] HelpButton.tsx created and configured
- [x] Development server running at http://localhost:5173
- [x] Slack-Sentry integration configured

## 🔍 Visual Testing Steps

### Step 1: Check Floating Help Button
1. **Visit**: http://localhost:5173
2. **Look for**: Blue floating help button in bottom-right corner
3. **Expected**: Circular blue button with help icon
4. **Test**: Hover to see "Need Help?" tooltip

### Step 2: Test Help Modal Opening
1. **Action**: Click the floating help button
2. **Expected**: Modal opens with "Need Help?" title
3. **Verify**: Form contains complaint categories and fields

### Step 3: Test Complaint Categories
Test each category to verify different alert routing:

#### 🐛 Bug Report Test
- **Select**: Bug Report category
- **Fill**: Title: "Test Bug Report"
- **Fill**: Description: "This is a test bug report to verify Sentry-Slack integration"
- **Fill**: Email: "test@example.com"
- **Priority**: High
- **Submit**: Click "Submit Request"
- **Expected**: Success message appears
- **Check**: Development team Slack channel for alert

#### 🚨 Urgent Issue Test
- **Select**: Urgent Issue category  
- **Fill**: Title: "Test Urgent Issue"
- **Fill**: Description: "This is a test urgent issue to verify immediate notifications"
- **Fill**: Email: "test@example.com"
- **Priority**: Urgent
- **Submit**: Click "Submit Request"
- **Expected**: Success message appears
- **Check**: Urgent Slack channel for immediate alert

#### 💡 Feature Request Test
- **Select**: Feature Request category
- **Fill**: Title: "Test Feature Request"
- **Fill**: Description: "This is a test feature request"
- **Fill**: Email: "test@example.com"
- **Priority**: Medium
- **Submit**: Click "Submit Request"
- **Expected**: Success message appears
- **Check**: Product team Slack channel for alert

#### ❓ General Help Test
- **Select**: General Help category
- **Fill**: Title: "Test General Help"
- **Fill**: Description: "This is a test help request"
- **Fill**: Email: "test@example.com"
- **Priority**: Low
- **Submit**: Click "Submit Request"
- **Expected**: Success message appears
- **Check**: Support team Slack channel for alert

## 📊 Sentry Event Verification

### Expected Sentry Events
For each complaint submission, verify in Sentry dashboard:

1. **User Feedback Event**
   - Event type: User Feedback
   - Email: Provided email address
   - Comments: Formatted complaint details

2. **Custom Message Event**
   - Message: "User Complaint: [Title]"
   - Level: 'error' for urgent, 'info' for others

### Expected Tags
- `user_complaint: true`
- `complaint_category: bug|feature|help|urgent`
- `complaint_priority: low|medium|high|urgent`
- `page_route: /` (or current page)

### Expected Context
- `complaint_details`: Rich context with URL, browser info, viewport
- User context with email

## 🔔 Slack Notification Verification

### Alert Rules to Check
1. **Urgent Complaints**
   - Condition: `user_complaint:true AND complaint_priority:urgent`
   - Should trigger: Immediate notification

2. **Bug Reports**
   - Condition: `user_complaint:true AND complaint_category:bug`
   - Should trigger: Development team alert

3. **All Complaints**
   - Condition: `user_complaint:true`
   - Should trigger: General notification

## ✅ Success Criteria

### Frontend Integration
- [  ] Floating help button visible and functional
- [  ] Modal opens and closes properly
- [  ] All complaint categories selectable
- [  ] Form validation working
- [  ] Success message displays after submission

### Sentry Integration  
- [  ] User feedback events created in Sentry
- [  ] Custom message events with proper tags
- [  ] Rich context data captured
- [  ] User information properly set

### Slack Notifications
- [  ] Urgent complaints trigger immediate alerts
- [  ] Bug reports alert development team
- [  ] Feature requests notify product team
- [  ] General help alerts support team

## 🐛 Troubleshooting

### If Help Button Not Visible
1. Check browser console for JavaScript errors
2. Verify HelpButton is imported and used in App.tsx
3. Check CSS z-index conflicts

### If Modal Doesn't Open
1. Check browser console for React errors
2. Verify HelpModal component import
3. Check state management in HelpButton

### If Sentry Events Not Created
1. Check Sentry DSN configuration
2. Verify network requests in browser dev tools
3. Check Sentry project settings

### If Slack Notifications Not Received
1. Verify Slack integration in Sentry dashboard
2. Check alert rule conditions
3. Verify Slack webhook configuration

## 🎉 Completion Status

Once all tests pass:
- ✅ User complaint system fully integrated
- ✅ Sentry monitoring operational
- ✅ Slack alerts configured and working
- ✅ Ready for production deployment

## 📞 Support

If any issues are encountered during testing:
1. Check browser console for errors
2. Review Sentry dashboard for events
3. Verify Slack channel activity
4. Test different browsers if needed

---

**System Status**: 🟢 Ready for Testing  
**Last Updated**: August 7, 2025  
**Version**: 1.0.0
