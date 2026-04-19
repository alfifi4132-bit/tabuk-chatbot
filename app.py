import streamlit as st
import time
import re
import difflib
from openai import OpenAI


# -----------------------------------
# إعدادات الصفحة
# -----------------------------------
st.set_page_config(
    page_title="شات بوت جامعة تبوك",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)
# -----------------------------------
# إعداد OpenAI
# -----------------------------------
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")

client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
# -----------------------------------
# بيانات أساسية
# -----------------------------------
UT_LOGO = "https://i0.wp.com/ksalogo.com/wp-content/uploads/2025/02/University-of-Tabuk-01-1.png?fit=1000%2C1000&ssl=1"

# -----------------------------------
# قاعدة الأسئلة والأجوبة
# عدّلي الإجابات من هنا فقط
# -----------------------------------
faq_items = {
    "summer_fees": {
        "button": "هل الفصل الصيفي مجاني؟",
        "question": "هل الفصل الصيفي برسوم مالية أم مجاني؟",
        "answer": "الفصل الصيفي مجاني للطلاب المنتظمين، ويبدأ التسجيل فيه حسب المواعيد التي تعلنها الجامعة سنويًا.",
        "patterns": [
            "هل الفصل الصيفي برسوم",
            "هل الصيفي برسوم",
            "هل الصيفي مجاني",
            "الصيفي مجاني",
            "الصيفي بفلوس",
            "الفصل الصيفي بفلوس",
            "رسوم الصيفي",
            "الفصل الصيفي مجاني",
            "هل الدراسة في الصيفي برسوم",
            "هل يوجد رسوم للفصل الصيفي"
        ]
    
    },
    "stipend_amount": {
    "question": "كم قيمة المكافأة الشهرية؟",
    "answer":" المكافأة الشهرية: 990 ريال للتخصصات العلمية، و840 ريال للتخصصات الأدبية.",
    "patterns": [
        "كم المكافاه",
        "كم قيمة المكافاه",
        "كم المكافاه الشهريه",
        "كم راتب الجامعه",
        "كم ينزل لي",
        "كم الفلوس",
        "كم المكافأة",
        "قيمة المكافأة",
        "كم تعطينا الجامعه",
        "كم يعطوني مكافاه",
        "المكافاه كم",
        "كم مبلغ المكافاه",
        "كم تنزل المكافاه فلوس",
        "كم ريال المكافاه",
        "كم المكافاه بالريال",
        "كم يعطون مكافاه الجامعه"
    ]
},

    "new_schedule_release": {
        "button": "متى ينزل الجدول الدراسي؟",
        "question": "متى ينزل الجدول الدراسي للفصل الجديد؟",
        "answer": "ينزل الجدول الدراسي للفصل الجديد قبل بداية الفصل وفق المواعيد الأكاديمية المعلنة، ويمكنك متابعته عبر البوابة الأكاديمية أو القنوات الرسمية للجامعة.",
        "patterns": [
            "متى ينزل الجدول",
            "متى ينزل الجدول الدراسي",
            "متى ينزل جدول الفصل الجديد",
            "موعد نزول الجدول",
            "متى يفتح الجدول",
            "متى اشوف جدولي",
            "متى يظهر الجدول الدراسي",
            "نزول الجدول الدراسي",
            "الجدول الدراسي متى ينزل"
        ]
    },

    "final_exam_schedule": {
        "button": "أين ألقى جدول الاختبارات؟",
        "question": "أين ألقى جدول الاختبارات النهائية؟",
        "answer": "يمكنك العثور على جدول الاختبارات النهائية من خلال البوابة الأكاديمية أو موقع الجامعة، وغالبًا يتم الإعلان عنه أيضًا عبر الكلية أو القسم الأكاديمي.",
        "patterns": [
            "اين القى جدول الاختبارات النهائيه",
            "وين القى جدول الاختبارات",
            "جدول الاختبارات النهائيه وين",
            "كيف اطلع جدول الاختبارات",
            "مكان جدول الاختبارات النهائيه",
            "ابي جدول الاختبارات النهائيه",
            "وين اشوف جدول الاختبارات",
            "جدول الفاينل وين"
        ]
    },

    "absence_limit": {
        "button": "كم نسبة الغياب؟",
        "question": "كم نسبة الغياب المسموحة قبل الحرمان؟",
        "answer": "نسبة الغياب هي 20% بدون عذر،و 35% مع عذر، وعند تجاوز النسبة المسموح بها يُحرم الطالب من دخول الاختبار النهائي للمقرر.",
        "patterns": [
            "كم نسبة الغياب",
            "نسبة الغياب",
            "الغياب المسموح",
            "كم الغياب المسموح",
            "قبل الحرمان كم نسبة الغياب",
            "متى انحرم بسبب الغياب",
            "كم غياب مسموح",
            "حد الغياب"
        ]
    },

    "absence_theory_practical": {
        "button": "هل تختلف نسبة الغياب؟",
        "question": "هل تختلف نسبة الغياب بين العملي والنظري؟",
        "answer": "قد تختلف آلية احتساب الغياب بين المقررات العملية والنظرية بحسب طبيعة المقرر واللائحة المعتمدة، لذلك الأفضل الرجوع إلى توصيف المقرر أو الكلية للتأكد من التفاصيل الخاصة بكل مادة.",
        "patterns": [
            "هل تختلف نسبة الغياب بين العملي والنظري",
            "غياب العملي مثل النظري",
            "هل العملي يختلف عن النظري في الغياب",
            "نسبة غياب العملي",
            "نسبة غياب النظري",
            "الحرمان في العملي مثل النظري"
        ]
    },

    "late_as_absence": {
        "button": "هل التأخير يحسب غياب؟",
        "question": "هل يُحسب التأخير كغياب؟",
        "answer": "قد يُحتسب التأخير كغياب أو يُسجل ضمن الملاحظات حسب سياسة عضو هيئة التدريس واللائحة المعتمدة للمقرر، لذلك يُفضّل الالتزام بوقت المحاضرة دائمًا.",
        "patterns": [
            "هل التاخير يحسب غياب",
            "التاخير غياب",
            "اذا تاخرت ينحسب غياب",
            "هل التأخير يعتبر غياب",
            "التاخر على المحاضره غياب",
            "التاخير في المحاضره هل يحسب"
        ]
    },

    "deprivation_honors": {
        "button": "هل الحرمان يؤثر على مرتبة الشرف؟",
        "question": "هل الحرمان يؤثر على مرتبة الشرف؟",
        "answer": "نعم، الحرمان قد يؤثر على مرتبة الشرف لأنه يؤثر على نتيجة الطالب في المقرر وعلى سجله الأكاديمي.",
        "patterns": [
            "هل الحرمان يؤثر على مرتبة الشرف",
            "الحرمان ومرتبة الشرف",
            "اذا انحرمت تروح مرتبة الشرف",
            "هل الحرمان يمنع مرتبة الشرف",
            "هل اقدر اخذ مرتبة شرف اذا انحرمت"
        ]
    },

    "attend_after_deprivation": {
        "button": "الحضور بعد الحرمان",
        "question": "هل يمكنني حضور المحاضرات بعد صدور قرار الحرمان؟",
        "answer": "بعد صدور قرار الحرمان من المقرر لا يستفيد الطالب أكاديميًا من الاستمرار في حضور المحاضرات لذلك ينبغي مراجعة القسم أو عضو هيئة التدريس لمعرفة الإجراء المتبع في المادة.",
        "patterns": [
            "هل اقدر احضر بعد الحرمان",
            "الحضور بعد الحرمان",
            "اذا انحرمت هل احضر",
            "هل استمر في الحضور بعد الحرمان",
            "بعد الحرمان اقدر ادخل المحاضرات"
        ]
    },

    "deprivation_one_subject": {
        "button": "الحرمان في مادة واحدة",
        "question": "هل الحرمان في مادة واحدة يؤثر على المواد الأخرى؟",
        "answer": "الحرمان في مادة واحدة يكون أثره على نفس المقرر غالبًا، ولا يعني حرمانًا تلقائيًا في بقية المواد، لكن قد يؤثر على المعدل والإنذار الأكاديمي بحسب الحالة.",
        "patterns": [
            "هل الحرمان في ماده وحده يؤثر على باقي المواد",
            "الحرمان في ماده يؤثر على المواد الثانيه",
            "اذا انحرمت في ماده هل اتاثر في باقي المواد",
            "حرمان ماده وحده",
            "الحرمان لماده واحده"
        ]
    },

    "miss_final_exam": {
        "button": "إذا غبت عن النهائي",
        "question": "ماذا يحدث إذا غبت عن الاختبار النهائي؟",
        "answer": "إذا غبت عن الاختبار النهائي دون عذر معتمد فقد تُرصد لك درجة الغياب في الاختبار، أما إذا كان لديك عذر رسمي فيجب تقديمه وفق الإجراءات والمدة المحددة من الجامعة.",
        "patterns": [
            "اذا غبت عن الاختبار النهائي",
            "غياب النهائي",
            "ما الذي يحدث اذا غبت عن النهائي",
            "لو ما حضرت النهائي",
            "اذا فاتني الاختبار النهائي",
            "ما حكم الغياب عن النهائي"
        ]
    },

    "retake_final_medical": {
        "button": "إعادة الاختبار بعذر طبي",
        "question": "هل يمكنني إعادة الاختبار إذا كان لدي عذر طبي؟",
        "answer": "نعم، يمكن النظر في حالتك إذا كان لديك عذر طبي معتمد، ويجب رفع العذر واتباع الإجراءات الرسمية خلال الفترة المحددة من الجامعة أو الكلية.",
        "patterns": [
            "هل اقدر اعيد الاختبار بعذر طبي",
            "اعادة الاختبار بعذر طبي",
            "اذا عندي عذر طبي اعيد النهائي",
            "هل في اختبار بديل بعذر طبي",
            "مرضت وقت الاختبار النهائي",
            "فاتني الاختبار وعندي تقرير طبي"
        ]
    },

    "stipend_date": {
        "button": "متى تنزل المكافأة؟",
        "question": "متى تنزل المكافأة الشهرية لطلاب جامعة تبوك؟",
        "answer": "تُصرف المكافأة الشهرية عادة يوم 27 من كل شهر.",
        "patterns": [
            "متى تنزل المكافاه",
            "موعد المكافاه",
            "متى تنزل المكافأة الشهريه",
            "نزول المكافاه",
            "راتب الجامعه متى ينزل",
            "متى تنزل الفلوس",
            "يوم كم تنزل المكافاه"
        ]
    },

    "stipend_summer": {
        "button": "المكافأة في الصيف",
        "question": "هل تنزل المكافأة في الإجازة الصيفية؟",
        "answer": "تستمر المكافأة في الصيف بحسب البيانات الحالية في البوت ما لم يوجد سبب أكاديمي أو إداري يؤدي إلى إيقافها.",
        "patterns": [
            "هل تنزل المكافاه في الصيف",
            "المكافاه في الاجازه الصيفيه",
            "هل المكافاه تستمر بالصيف",
            "تنزل المكافاه بالصيف",
            "المكافاه وقت الاجازه الصيفيه"
        ]
    },
    "stipend_cut_reasons": {
        "button": "أسباب قطع المكافأة",
        "question": "ما هي الأسباب التي تؤدي إلى قطع المكافأة الشهرية؟",
        "answer": "من أبرز أسباب قطع المكافأة: الانقطاع عن الدراسة، أو وجود سبب أكاديمي أو إداري مؤثر، أو عدم تحقيق الشروط المستمرة للاستحقاق بحسب الأنظمة المعتمدة.",
        "patterns": [
            "اسباب قطع المكافاه",
            "ليش تنقطع المكافاه",
            "متى تنقطع المكافاه",
            "ما اسباب ايقاف المكافاه",
            "ايش يوقف المكافاه",
            "اسباب حرمان المكافاه"
        ]
    },

    "stipend_gpa": {
        "button": "هل تنقطع إذا المعدل أقل من 2؟",
        "question": "هل تنقطع المكافأة إذا نزل معدلي عن 2.00؟",
        "answer": "بحسب البيانات الحالية في البوت، قد تتأثر المكافأة إذا نزل المعدل عن 2.00، لذلك يُنصح بمتابعة الحالة الأكاديمية والرجوع للوائح الاستحقاق المعتمدة.",
        "patterns": [
            "هل تنقطع المكافاه اذا نزل معدلي عن 2",
            "اذا المعدل اقل من 2 تنقطع المكافاه",
            "المكافاه ومعدل 2",
            "نزول المعدل تحت 2 هل يوقف المكافاه",
            "لو معدلي 1.99 تنقطع المكافاه"
        ]
    },

    "applied_college_majors": {
        "button": "تخصصات الكلية التطبيقية",
        "question": "ما هي التخصصات المتاحة في الكلية التطبيقية بتبوك لهذا العام؟",
        "answer": "تخصصات الكلية التطبيقية تتحدد سنويًا حسب البرامج المطروحة، ومنها"
        ",'برمجه وعلوم حاسب - ادارة أنظمة الشبكات -مكافحة عدوى- موارد بشرية - تأمين ومخاطر'"
        " ويمكنك معرفة التخصصات المتاحة لهذا العام من خلال بوابة القبول أو موقع الكلية التطبيقية بجامعة تبوك.",
        "patterns": [
            "ما هي التخصصات المتاحه في الكليه التطبيقيه",
            "تخصصات الكليه التطبيقيه",
            "وش تخصصات التطبيقية",
            "التخصصات المتاحه في التطبيقية",
            "برامج الكليه التطبيقيه",
            "الكليه التطبيقيه فيها ايش تخصصات"
        ]
    },

    "diploma_difference": {
        "button": "الفرق بين الدبلومين",
        "question": "ما الفرق بين الدبلوم المتوسط والدبلوم المشارك؟",
        "answer": "الفرق بين الدبلوم المتوسط والدبلوم المشارك يكون في الخطة الدراسية وعدد الساعات والمخرجات التعليمية بحسب البرنامج المعتمد، لذلك الأفضل الرجوع لوصف كل برنامج لمعرفة الفروقات الدقيقة.",
        "patterns": [
            "ما الفرق بين الدبلوم المتوسط والدبلوم المشارك",
            "الفرق بين الدبلوم المتوسط والمشارك",
            "وش الفرق بين الدبلومين",
            "يعني ايش دبلوم مشارك",
            "يعني ايش دبلوم متوسط",
            "الفرق بين المشارك والمتوسط"
        ]
    },

    "applied_college_duration": {
        "button": "مدة الدراسة في التطبيقية",
        "question": "ما هي مدة الدراسة في برامج الكلية التطبيقية؟",
        "answer": "مدة الدراسة في برامج الكلية التطبيقية تختلف حسب البرنامج والخطة الدراسية، وتُحدد في الوصف الأكاديمي لكل برنامج عند طرحه.",
        "patterns": [
            "كم مدة الدراسه في الكليه التطبيقيه",
            "مدة الدراسة في التطبيقية",
            "كم سنه في الكليه التطبيقيه",
            "برامج التطبيقية كم مدتها",
            "الدبلوم في التطبيقية كم ترم"
        ]
    },

    "bridge_to_bachelor": {
        "button": "إكمال البكالوريوس بعد التطبيقية",
        "question": "هل يمكنني إكمال دراسة البكالوريوس بعد التخرج من الكلية التطبيقية؟",
        "answer": "نعم، يمكن إكمال دراسة البكالوريوس بعد التخرج من الكلية التطبيقية إذا كان هناك مسار تجسير أو برامج إكمال معتمدة وتنطبق عليك شروط القبول الخاصة بها.",
        "patterns": [
            "هل اقدر اكمل بكالوريوس بعد الكليه التطبيقيه",
            "اكمال البكالوريوس بعد التطبيقية",
            "التجسير بعد التطبيقية",
            "هل فيه تجسير بعد الدبلوم",
            "اقدر اكمل بعد التخرج من التطبيقية",
            "بعد الدبلوم اقدر اكمل بكالوريوس"
        ]
    },
}

# -----------------------------------
# تجميع كلمات مفتاحية إضافية
# -----------------------------------
general_fallback_keywords = {
    "summer_fees": ["صيفي", "الصيفي", "رسوم", "مجاني"],
    "new_schedule_release": ["الجدول", "الدراسي", "الفصل", "الجديد"],
    "final_exam_schedule": ["جدول", "الاختبارات", "النهائيه", "النهائي"],
    "absence_limit": ["غياب", "نسبه", "حرمان"],
    "absence_theory_practical": ["غياب", "عملي", "نظري"],
    "late_as_absence": ["تأخير", "تاخير", "غياب"],
    "deprivation_honors": ["حرمان", "مرتبه", "الشرف"],
    "attend_after_deprivation": ["حضور", "محاضرات", "بعد", "الحرمان"],
    "deprivation_one_subject": ["حرمان", "ماده", "المواد"],
    "miss_final_exam": ["غبت", "الاختبار", "النهائي"],
    "retake_final_medical": ["اعاده", "اختبار", "عذر", "طبي"],
    "stipend_date": ["مكافاه", "متى", "تنزل"],
    "stipend_summer": ["مكافاه", "الصيف", "الاجازه"],
    "stipend_cut_reasons": ["اسباب", "قطع", "المكافاه"],
    "stipend_gpa": ["معدل", "2", "المكافاه"],
    "applied_college_majors": ["الكليه", "التطبيقيه", "تخصصات"],
    "diploma_difference": ["دبلوم", "متوسط", "مشارك"],
    "applied_college_duration": ["مده", "الدراسه", "التطبيقيه"],
    "bridge_to_bachelor": ["اكمل", "بكالوريوس", "تجسير", "التطبيقيه"],
    "stipend_amount": ["مكافاه", "كم", "ريال", "فلوس", "راتب"],
}

# -----------------------------------
# الأسئلة الجانبية
# -----------------------------------

# -----------------------------------
# حالة الجلسة
# -----------------------------------
if "welcome" not in st.session_state:
    st.session_state.welcome = True

if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------------
# CSS
# -----------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Readex+Pro:wght@300;400;500;600;700;800&family=El+Messiri:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Readex Pro', sans-serif;
}

.stApp {
    direction: rtl;
    background:
        radial-gradient(circle at top right, rgba(212,175,55,0.14), transparent 18%),
        radial-gradient(circle at top left, rgba(26,74,62,0.10), transparent 22%),
        linear-gradient(180deg, #f9fbfa 0%, #f4f7f5 48%, #eef3f1 100%);
    background-attachment: fixed;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    max-width: 1280px;
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

h1, h2, h3 {
    font-family: 'El Messiri', sans-serif !important;
}

.main-top-line {
    height: 6px;
    border-radius: 999px;
    margin-bottom: 22px;
    background: linear-gradient(90deg, #d4af37 0%, #f3dc8f 45%, #1f5a4b 100%);
    box-shadow: 0 4px 12px rgba(212,175,55,0.18);
}

.welcome-main-wrap {
    text-align: center;
    padding-top: 40px;
    padding-bottom: 20px;
}

.welcome-main-title {
    font-family: 'El Messiri', sans-serif;
    font-size: 52px;
    font-weight: 700;
    color: #2d4d45;
    margin-bottom: 10px;
    text-shadow: 0 2px 10px rgba(0,0,0,0.06);
}

.cap-icon {
    text-align: center;
    font-size: 34px;
    margin-top: 4px;
    margin-bottom: 10px;
}

.gold-line {
    width: 150px;
    height: 8px;
    margin: 0 auto 18px auto;
    border-radius: 999px;
    background: linear-gradient(90deg, rgba(212,175,55,0.0), rgba(212,175,55,0.88), rgba(212,175,55,0.0));
}

.first-footer-card {
    background: linear-gradient(135deg, #173f35 0%, #215447 52%, #2f7360 100%);
    color: white;
    border-radius: 30px;
    padding: 30px 24px;
    box-shadow: 0 18px 36px rgba(12,38,32,0.16);
    text-align: center;
}

.first-footer-big-title {
    font-family: 'El Messiri', sans-serif;
    font-size: 30px;
    font-weight: 700;
    margin-bottom: 12px;
    color: white;
}

.first-footer-text {
    margin: 0 0 10px 0;
    line-height: 1.9;
    opacity: 0.95;
    font-size: 15px;
}

.first-footer-copy {
    margin: 0;
    opacity: 0.78;
    font-size: 13px;
}

.hero-card {
    background: linear-gradient(135deg, rgba(16,45,39,0.98) 0%, rgba(23,63,53,0.96) 50%, rgba(44,110,92,0.96) 100%);
    color: white;
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 30px;
    padding: 30px 28px;
    box-shadow: 0 22px 46px rgba(10,35,30,0.18), inset 0 1px 0 rgba(255,255,255,0.08);
    margin-bottom: 24px;
}

.info-box {
            background: linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(255,255,255,0.84) 100%);
    border: 1px solid rgba(26,74,62,0.08);
    border-radius: 20px;
    padding: 14px 12px;
    min-height: 140px;
    box-shadow: 0 10px 20px rgba(0,0,0,0.04);
}

.info-top-line {
    height: 4px;
    border-radius: 999px;
    margin-bottom: 14px;
    background: linear-gradient(90deg, #d4af37, #f3df98, #1f5a4b);
}

.section-label {
    font-family: 'El Messiri', sans-serif;
    font-size: 24px;
    font-weight: 700;
    color: #1a4a3e;
    margin-bottom: 12px;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #173f35 0%, #11322b 58%, #0d2621 100%);
    border-left: 1px solid rgba(255,255,255,0.06);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.sidebar-logo-box {
    background: linear-gradient(135deg, rgba(255,255,255,0.18), rgba(255,255,255,0.08));
    border: 1px solid rgba(255,255,255,0.35);
    padding: 16px;
    border-radius: 28px;
    box-shadow:
        0 14px 26px rgba(0,0,0,0.12),
        inset 0 1px 0 rgba(255,255,255,0.14);
    backdrop-filter: blur(6px);
    text-align: center;
    margin-bottom: 16px;
}

.sidebar-info-box {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 24px;
    padding: 16px;
    margin-top: 16px;
    margin-bottom: 18px;
    text-align: center;
}

.stButton > button {
    width: 100%;
    border: 1px solid rgba(212,175,55,0.35);
    border-radius: 18px;
    padding: 0.85rem 1rem;
    background: linear-gradient(135deg, #d4af37 0%, #f0d77a 45%, #f8e8aa 100%);
    color: #143a31 !important;
    font-weight: 800;
    font-size: 15px;
    box-shadow:
        0 10px 20px rgba(212,175,55,0.18),
        inset 0 1px 0 rgba(255,255,255,0.70);
    transition: all 0.25s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow:
        0 14px 24px rgba(212,175,55,0.28),
        inset 0 1px 0 rgba(255,255,255,0.82);
}

[data-testid="stChatMessage"] {
    border-radius: 24px;
    padding: 12px 16px;
    margin-bottom: 12px;
    box-shadow: 0 10px 24px rgba(0,0,0,0.05), inset 0 1px 0 rgba(255,255,255,0.56);
    overflow: hidden;
}

[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, rgba(26,74,62,0.12), rgba(26,74,62,0.05));
    border: 1px solid rgba(26,74,62,0.10);
}

[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
    background: linear-gradient(180deg, rgba(255,255,255,0.93), rgba(255,255,255,0.80));
    border: 1px solid rgba(212,175,55,0.20);
}

.stChatInputContainer {
    border-top: none !important;
}

[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.90);
    border-radius: 20px;
}

div[data-testid="stChatInput"] > div {
    border: 1px solid rgba(26,74,62,0.10);
    border-radius: 18px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.04), inset 0 1px 0 rgba(255,255,255,0.76);
}

@media (max-width: 900px) {
    .welcome-main-title {
        font-size: 30px;
    }
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# دوال مساعدة
# -----------------------------------
def normalize_text(text):
    if not text:
        return ""

    text = str(text).strip().lower()

    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ة": "ه",
        "ى": "ي",
        "ؤ": "و",
        "ئ": "ي",
        "ـ": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # إزالة التشكيل
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)

    # إزالة الرموز
    text = re.sub(r"[^\w\s]", " ", text)

    # توحيد المسافات
    text = re.sub(r"\s+", " ", text).strip()

    return text

def tokenize(text):
    return normalize_text(text).split()

def similarity(a, b):
    return difflib.SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()

def match_question(user_input):
    user_norm = normalize_text(user_input)
    user_tokens = set(tokenize(user_input))
    best_id = None
    best_score = 0

    for item_id, item in faq_items.items():
        score = 0

        # 1) مطابقات مباشرة لعبارات معروفة
        for pattern in item["patterns"]:
            pattern_norm = normalize_text(pattern)

            if pattern_norm in user_norm:
                score += 8

            sim = similarity(user_norm, pattern_norm)
            if sim >= 0.92:
                score += 8
            elif sim >= 0.85:
                score += 6
            elif sim >= 0.75:
                score += 4

        # 2) مطابقة السؤال الأساسي
        q_sim = similarity(user_norm, item["question"])
        if q_sim >= 0.90:
            score += 8
        elif q_sim >= 0.80:
            score += 5
        elif q_sim >= 0.70:
            score += 3

        # 3) مطابقة الكلمات المفتاحية
        fallback_keywords = general_fallback_keywords.get(item_id, [])
        overlap = sum(1 for kw in fallback_keywords if normalize_text(kw) in user_norm or normalize_text(kw) in user_tokens)
        score += overlap * 2

        # 4) بونص إذا اجتمعت كلمات مهمة
        if len(fallback_keywords) > 0:
            matched_tokens = sum(1 for kw in fallback_keywords if normalize_text(kw) in user_norm)
            if matched_tokens >= 2:
                score += 2
            if matched_tokens >= 3:
                score += 2

        if score > best_score:
            best_score = score
            best_id = item_id

    # عتبة القبول
    if best_score >= 5:
        return best_id

    return None

def quick_reply(topic_name):
    st.session_state.messages.append({
        "role": "user",
        "content": sidebar_topics[topic_name]["question"]
    })
    st.session_state.messages.append({
        "role": "assistant",
        "content": sidebar_topics[topic_name]["answer"]
    })
    st.rerun()
def ask_smart_assistant(user_question):
    if client is None:
        return None

    try:
        response = client.responses.create(
            model="gpt-5.4",
            instructions=(
                "أنت مساعد ذكي خاص بجامعة تبوك. "
                "أجب بالعربية فقط. "
                "إذا كان السؤال عن جامعة تبوك أو الأنظمة الأكاديمية أو المكافآت أو الغياب أو الكلية التطبيقية، "
                "فأجب بطريقة واضحة ومرتبة ومختصرة ومفيدة. "
                "إذا كانت المعلومة غير مؤكدة فلا تخترع معلومات، واذكر ذلك بصراحة."
            ),
            input=user_question
        )
        return response.output_text.strip()

    except Exception:
        return None
# -----------------------------------
# الصفحة الأولى
# -----------------------------------
if st.session_state.welcome:
    st.markdown('<div class="main-top-line"></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center; margin-bottom:10px;">
        <img src="{UT_LOGO}" width="150">
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="welcome-main-wrap">
        <div class="welcome-main-title">أهلاً بكِ في شات بوت جامعة تبوك</div>
        <div class="cap-icon">🎓</div>
        <div class="gold-line"></div>
    </div>
    """, unsafe_allow_html=True)

    b1, b2, b3 = st.columns([1, 1, 1])
    with b2:
        if st.button("🎓 ادخل إلى بوت الجامعة"):
            st.session_state.welcome = False
            st.rerun()

    st.write("")
    st.write("")

    f1, f2, f3 = st.columns([1, 1.7, 1])
    with f2:
        st.markdown("""
        <div class="first-footer-card">
            <div class="first-footer-big-title">✨ بوابتك الذكية لجامعة تبوك ✨</div>
            <div class="first-footer-text">
                شات بوت جامعي ذكي يساعدكِ في الوصول إلى المعلومات بسرعة وسهولة.
            </div>
            <div class="first-footer-copy">
                ©️ 2026 جميع الحقوق محفوظة - جامعة تبوك
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.stop()

# -----------------------------------
# مواضيع السايدبار فقط (ترجع مثل قبل)
# -----------------------------------
sidebar_topics = {
    "الصيفي": {
        "question": "هل الفصل الصيفي برسوم مالية أم مجاني؟",
        "answer": "الفصل الصيفي مجاني للطلاب المنتظمين، ويبدأ التسجيل فيه حسب المواعيد التي تعلنها الجامعة سنويًا."
    },
    "المكافأة": {
        "question": "متى تنزل المكافأة الشهرية لطلاب جامعة تبوك؟",
        "answer": "تُصرف المكافأة الشهرية عادة يوم 27 من كل شهر."
    },
    "الغياب": {
        "question": "كم نسبة الغياب المسموحة قبل الحرمان؟",
        "answer": "نسبة الغياب المسموحة قبل الحرمان هي 20% بحسب البيانات الحالية في البوت، وعند تجاوز النسبة المسموح بها يُحرم الطالب من دخول الاختبار النهائي للمقرر."
    },
    "الكلية التطبيقية": {
        "question": "ما هي التخصصات المتاحة في الكلية التطبيقية بتبوك لهذا العام؟",
        "answer": "تخصصات الكلية التطبيقية تتحدد سنويًا حسب البرامج المطروحة، ويمكنك معرفة التخصصات المتاحة لهذا العام من خلال بوابة القبول أو موقع الكلية التطبيقية بجامعة تبوك."
    }
}
# -----------------------------------
# السايدبار
# -----------------------------------
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-logo-box">
        <img src="{UT_LOGO}" width="90">
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-info-box">
        <h3 style="margin-top:0; margin-bottom:8px;">📌 الاستفسارات الشائعة</h3>
        <p style="margin:0; font-size:14px; opacity:0.92; line-height:1.9;">
            اختاري من الموضوعات التالية للحصول على إجابة فورية داخل البوت الجامعي.
        </p>
    </div>
    """, unsafe_allow_html=True)

    for topic_name in sidebar_topics:
        if st.button(f"✨ {topic_name}"):
            quick_reply(topic_name)
# -----------------------------------
# الصفحة الثانية
# -----------------------------------
st.markdown('<div class="main-top-line"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="hero-card">
           <div style="text-align:center;">
        <h1 style="margin:0; color:white;">🎓 نظام الاستفسار الذكي - جامعة تبوك</h1>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="info-box">
        <div class="info-top-line"></div>
        <div style="font-size:24px; margin-bottom:8px;">⚡</div>
        <h3 style="margin:0 0 6px 0; color:#1a4a3e; font-size:18px;">سرعة الوصول</h3>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="info-box">
        <div class="info-top-line"></div>
        <div style="font-size:24px; margin-bottom:8px;">🎯</div>
        <h3 style="margin:0 0 6px 0; color:#1a4a3e; font-size:18px;">وضوح المعلومات</h3>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="info-box">
        <div class="info-top-line"></div>
        <div style="font-size:24px; margin-bottom:8px;">💎</div>
        <h3 style="margin:0 0 6px 0; color:#1a4a3e; font-size:18px;">تجربة احترافية</h3>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.markdown('<div class="section-label">المحادثة</div>', unsafe_allow_html=True)

# -----------------------------------
# عرض الرسائل
# -----------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------------
# إدخال المستخدم
# -----------------------------------
if prompt := st.chat_input("اكتبي سؤالك هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        matched_id = match_question(prompt)

        if matched_id:
            response = faq_items[matched_id]["answer"]
        else:
            smart_response = ask_smart_assistant(prompt)

            if smart_response:
                response = smart_response
            else:
                response = (
                    "أعتذر، لم تتضح لي صياغة السؤال بالكامل 🌷\n\n"
                    "يمكنكِ السؤال بصيغة أخرى مثل:\n"
                    "- هل الصيفي مجاني؟\n"
                    "- متى ينزل الجدول؟\n"
                    "- كم نسبة الغياب؟\n"
                    "- متى تنزل المكافأة؟\n"
                    "- هل أقدر أكمل بكالوريوس بعد التطبيقية؟"
                )

        message_placeholder = st.empty()
        full_response = ""

        for chunk in response.split():
            full_response += chunk + " "
            time.sleep(0.03)
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response.strip())
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response.strip()
        })