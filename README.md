# AI Customer Review Agent

This application is a review platform where an AI agent, Ernest, gathers reviews by interacting with customers, instead of customers creating their own content.

Unlike other chatbots that rely on predefined questions, Ernest can **dynamically generate queries based on customer responses**. Ernest is also capable of:

- Determining when to delve deeper into the current topic or shift to different questions, based on the customer's response.
- Deciding whether to merely react or to react and ask a follow-up question.
- Operating with a local Llama 3 model.
- Collecting the context of user information.
- Referencing other users' reviews on the same topic (e.g., AI: "Oh yeah, I’ve heard the same complaint from 3 other customers. I think this is a common issue.")

The front end of this application is developed using the Vercel AI SDK, which promotes rapid and clean development. For the backend server, [Modal](http://modal.com/) is selected because of its quick cold start and efficient GPU utilization.