<div align="center">

<img src="assets/logo.png" width="120" alt="شعار مساري">

# مساري · Masari

**مرشدك المهني الذكي على تليجرام**

وكيل ذكاء اصطناعي يساعد الخريجين والباحثين عن عمل على اكتشاف مسارهم المهني، ومراجعة سيرهم الذاتية، والتدرب على المقابلات، وبناء خطة تعلم. مبني بالكامل على **n8n** بدون كتابة كود.

[![جرّب البوت](https://img.shields.io/badge/Telegram-@MasariCareerBot-26A5E4?logo=telegram&logoColor=white)](https://t.me/MasariCareerBot)
[![صفحة المشروع](https://img.shields.io/badge/%D8%B5%D9%81%D8%AD%D8%A9%20%D8%A7%D9%84%D9%85%D8%B4%D8%B1%D9%88%D8%B9-GitHub%20Pages-0f8f86)](https://aj5749843-cmd.github.io/masari-career-bot/)
[![n8n](https://img.shields.io/badge/Built%20with-n8n-EA4B71?logo=n8n&logoColor=white)](https://n8n.io)
[![Gemini](https://img.shields.io/badge/LLM-Google%20Gemini-4285F4?logo=googlegemini&logoColor=white)](https://ai.google.dev)

<img src="assets/demo.gif" width="760" alt="عرض متحرك لمساري">

</div>

---

## الفكرة

كثير من الخريجين يعرفون ما درسوا، ولا يعرفون أين يتجهون. والإرشاد المهني الجيد يحتاج وقتاً وجلسات فردية لا تتوفر لكل من يحتاجها. **مساري** يقدّم هذا الإرشاد في محادثة واحدة على تليجرام، بالعربية، ومجاناً.

## الخدمات

| الأمر | الخدمة | ما يحصل عليه المستخدم |
|---|---|---|
| `/assess` | اكتشف مسارك | محادثة من 6 إلى 8 أسئلة، ثم تقرير بثلاثة مسارات مهنية في سوق العمل السعودي، لكل منها المهارات المطلوبة وشهادة للبدء وخطوة عملية |
| `/interview` | محاكاة مقابلة عمل | مقابلة من 6 أسئلة، ثم تقييم من 10 وملاحظة على كل إجابة ونموذج إجابة بطريقة STAR |
| `/cv` | مراجعة السيرة الذاتية | تقييم عام، وأهم 5 تحسينات مع إعادة صياغة، والكلمات المفتاحية الناقصة لأنظمة ATS |
| `/plan` | خطة تعلم | 3 إلى 4 مراحل لكل منها مخرج ملموس، ومشروع تطبيقي لملف الأعمال |
| `/end` | إنهاء المقابلة | يستلم المستخدم تقرير المقابلة فوراً |

يتذكر مساري ما قاله المستخدم خلال المحادثة، فتبني كل خدمة على ما قبلها دون تكرار الأسئلة.

## كيف يعمل

```mermaid
flowchart RL
    A[Telegram Trigger<br/>تستقبل الرسالة] --> B{/start أو /help؟}
    B -- نعم --> C[Send Welcome<br/>رسالة الترحيب]
    B -- لا --> D[Typing...<br/>مؤشر الكتابة]
    D --> E[Masari Agent<br/>AI Agent]
    F[(Google Gemini<br/>النموذج اللغوي)] -.-> E
    G[(Window Memory<br/>ذاكرة لكل مستخدم)] -.-> E
    E --> H[Send Reply<br/>الرد]
```

سير عمل من ثماني عقد على n8n. تعليمات الوكيل كاملة في [`prompts/system-prompt.md`](prompts/system-prompt.md).

## ضوابط التصميم

- **الدقة:** لا يخترع أرقام رواتب أو شروط قبول، ويحيل المستخدم دائماً إلى المصادر الرسمية.
- **الخصوصية:** ينبّه المستخدم ألا يشارك رقم هويته أو أي بيانات حساسة، ولكل مستخدم ذاكرة منفصلة.
- **الفئة العمرية:** الخدمة لمن هم 18 سنة فأكثر، ومن هو دون ذلك يُوجَّه بلطف إلى المرشد الطلابي ووالديه.

## لقطات

<p align="center">
<img src="assets/screenshots/assess.png" width="32%" alt="اكتشاف المسار">
<img src="assets/screenshots/report.png" width="32%" alt="تقرير المقابلة">
<img src="assets/screenshots/age.png" width="32%" alt="الالتزام بالفئة العمرية">
</p>

## التشغيل

1. أنشئ بوتاً من [@BotFather](https://t.me/BotFather) واحصل على التوكن.
2. احصل على مفتاح Gemini API من [Google AI Studio](https://aistudio.google.com).
3. استورد [`workflow/masari-workflow.json`](workflow/) في n8n، واربط الحسابين، ثم انشر سير العمل.

الخطوات التفصيلية وحل المشكلات في [`guides/setup-guide.md`](guides/setup-guide.md).

## محتويات المستودع

| المسار | المحتوى |
|---|---|
| `workflow/` | سير عمل n8n الجاهز للاستيراد |
| `prompts/` | تعليمات الوكيل ورسالة الترحيب وقائمة الأوامر |
| `guides/` | دليل التشغيل خطوة بخطوة |
| `docs/` | صفحة المشروع (تُنشر عبر GitHub Pages) |
| `assets/` | الشعار واللقطات والفيديوهات الترويجية |
| `video-source/` | مصدر الفيديوهات الترويجية (رسوم HTML وموسيقى مولّدة برمجياً) |

## الخطوات القادمة

- [ ] قراءة السيرة الذاتية مباشرة من ملف PDF أو صورة
- [ ] حفظ الملف المهني لكل مستخدم في قاعدة بيانات
- [ ] ذاكرة دائمة تبقى بعد إعادة تشغيل الخادم
- [ ] حد يومي للرسائل لضبط الاستخدام

---

<div align="center">

فكرة وتصميم وتنفيذ **أريج عطاالله الجبرتي** · 2026

</div>

---

<details>
<summary><b>English summary</b></summary>

**Masari** is an Arabic AI career-guidance agent on Telegram for graduates and job seekers (18+) in Saudi Arabia. Built entirely in **n8n** with no code: Telegram Trigger → AI Agent (Google Gemini + per-user window memory) → reply.

Commands: `/assess` (career path discovery with a 3-path report), `/interview` (6-question mock interview with a STAR-based report), `/cv` (CV review with ATS keyword gaps), `/plan` (staged learning plan).

Guardrails: no invented salaries or admission requirements, privacy reminders, and an 18+ age policy that politely redirects younger users to their school counselor.

Try it: [t.me/MasariCareerBot](https://t.me/MasariCareerBot)
</details>
