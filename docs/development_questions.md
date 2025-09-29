# CoreSync Development Questions

Based on the detailed UX scenarios provided, we need clarification on the following technical and functional requirements to proceed with development:

## 🔐 Authentication & Security

1. **Face Recognition Technology:**
   - Which face recognition provider should we integrate? (AWS Rekognition, Azure Face API, custom solution)
   - Do you have existing hardware for face recognition kiosks, or should we recommend specific devices?
   - What's the backup authentication method if face recognition fails?

2. **Biometric Data Storage:**
   - Where should biometric data be stored? (local device, encrypted cloud, on-premise)
   - What are your data retention policies for biometric information?
   - Do you need GDPR/CCPA compliance for biometric data?

3. **Member Authentication:**
   - Should non-members be able to browse services in read-only mode before signing up?
   - What information is required during the membership signup process?
   - How do you handle family memberships or shared accounts?

## 💳 Payment & Billing

4. **Card-on-File System:**
   - Should we use Stripe Customer Portal for card management, or build a custom solution?
   - What's the maximum amount that can be charged without additional verification?
   - How do you handle failed payments or expired cards?

5. **Concierge Requests:**
   - What's the maximum budget limit for concierge requests?
   - Who approves high-value requests ($500+)?
   - How far in advance can concierge items be ordered?
   - Should there be spending limits per membership tier?

## 🏢 Equipment & IoT Integration

6. **Equipment Specifications:**
   - Can you provide the complete list of IoT equipment with API documentation?
   - Which equipment supports remote control vs. manual operation?
   - Are there safety protocols for remote equipment control?

7. **Specific Equipment Questions:**
   - **AI Massage Beds:** How many preset programs? Can users create custom programs?
   - **Meditation Pods:** What breathwork programs are available? Integration with existing meditation apps?
   - **Oxygen Dome:** Safety protocols for automated control?
   - **Immersive Screens:** Display resolution and supported formats?

## 🎬 Content & Media

8. **Immersive Scene Library:**
   - Do you have existing 4K/8K content library, or should we source/create it?
   - Which immersive scenes are priorities? (Alps, Venice, Ocean, etc.)
   - Can members upload their own content? What file formats/size limits?
   - Do you need content licensing for third-party media?

9. **Personal Media:**
   - Should we integrate with Spotify/Apple Music for personal playlists?
   - What's the maximum storage per user for uploaded content?
   - Are there content moderation requirements for user uploads?

## 🤖 AI & Recommendations

10. **AI Recommendation Engine:**
    - What data should the AI use for recommendations? (service history, frequency, health goals)
    - How often should AI recommendations be updated?
    - Should AI consider seasonal factors or member's calendar?
    - Do you want predictive booking suggestions?

11. **Personalization Data:**
    - What member preferences should be tracked? (temperature, lighting, scents, music)
    - How granular should the customization be?
    - Should preferences sync across different room types?

## 📅 Booking & Scheduling

12. **Priority Booking:**
    - How many days in advance can priority members book vs. regular members?
    - What happens when priority and regular bookings conflict?
    - Can members book multiple services in sequence?

13. **Service Combinations:**
    - Which services can be combined in a single booking?
    - Are there time restrictions between certain services?
    - Should the app suggest optimal service sequences?

## 🛍️ Retail & Concierge

14. **Spa Shop:**
    - Do you have an existing product catalog/PIM system?
    - How long should purchased items be held for pickup?
    - Should members be notified when their items are ready?
    - What happens to unpicked items after a certain period?

15. **Concierge Service:**
    - What types of items can be requested? (alcohol, flowers, food, luxury goods)
    - Do you have preferred suppliers/vendors?
    - What's the typical fulfillment time for different request types?
    - Should there be request categories with different approval processes?

## 🏠 Facility Management

16. **Room & Space Management:**
    - Can you provide exact room names and capacities?
    - Which rooms have which equipment/amenities?
    - How should the app handle room availability conflicts?

17. **Backyard Reservation:**
    - Is the backyard a separate bookable space or part of Coresync Private?
    - What are the capacity limits and time slots?
    - Are there weather-related cancellation policies?

## 💰 Investment Portal

18. **Investor Features:**
    - Who should have access to the investment portal? (all members, specific tiers, invitation only)
    - What types of documents should be accessible? (financial reports, investment opportunities)
    - Do you need accredited investor verification?
    - Should investment tracking be integrated with member profiles?

## 📱 Technical Requirements

19. **Offline Functionality:**
    - Which features should work offline? (member profile, preferences, basic booking info)
    - How should the app sync when connectivity is restored?
    - What's the offline data storage limit?

20. **Performance & Scalability:**
    - Expected number of concurrent users during peak hours?
    - Target response time for booking operations?
    - Should we implement real-time notifications for equipment status?

## 🔔 Notifications & Communication

21. **Push Notifications:**
    - What types of notifications should be sent? (booking reminders, AI recommendations, special offers)
    - How often can marketing notifications be sent?
    - Should notifications be personalized by membership tier?

22. **Member Communication:**
    - Should the app include in-app messaging with spa staff?
    - How do you want to handle customer service inquiries?
    - Should there be automated responses for common questions?

## 📊 Analytics & Reporting

23. **Admin Dashboard:**
    - What metrics are most important for daily operations?
    - Should the dashboard show real-time equipment status?
    - Do you need custom reporting features?

24. **Member Analytics:**
    - What data should be tracked for each member? (visit frequency, spending patterns, preferences)
    - Should members see their own usage analytics?
    - Do you need integration with existing CRM systems?

## 🚀 Launch & Deployment

25. **Rollout Strategy:**
    - Should we launch with limited features and gradually add more?
    - Do you want a beta testing period with select members?
    - What's the priority order for implementing features?

26. **Integration Timeline:**
    - Which integrations are critical for Phase 1 launch?
    - Can some advanced features (AI, immersive content) be Phase 2?
    - Do you have existing systems that need to be integrated?

---

## Priority Classification

**Critical for MVP (Phase 1):**
- Questions 1-3, 4-5, 6-7, 12-13, 16-17, 25-26

**Important for Full Launch (Phase 2):**
- Questions 8-11, 14-15, 18-24

**Nice to Have (Future Phases):**
- Advanced AI features, complex content management, detailed analytics

Please prioritize your responses based on which features are most critical for your launch timeline.
