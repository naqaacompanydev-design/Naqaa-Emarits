"""Location pages. Each entry builds /locations/<slug>/ and /ar/locations/<slug>/.

  name      emirate name (quote form, schema areaServed)
  h1_short  footer link text
  areas     neighbourhoods shown as chips. TODO: confirm with the owner which areas are covered.
  body      (h2, html) sections specific to this emirate
"""

LOCATIONS = [
  {
    "slug": "dubai",
    "en": {
      "name": "Dubai", "h1_short": "Cleaning in Dubai",
      "title": "Cleaning Company in Dubai | Home & Villa Cleaning | Naqaa",
      "desc": "Home, deep, move-out, sofa and office cleaning across Dubai: Marina, JVC, Downtown, Al Barsha and more. Clear price on WhatsApp before booking.",
      "h1": "Cleaning company in Dubai",
      "lead": "Apartments in towers, villas in gated communities and offices in business districts. Our teams cover Dubai from the Marina to Mirdif, with materials and equipment included.",
      "areas": ["Dubai Marina", "JLT", "JVC", "Downtown Dubai", "Business Bay", "Al Barsha", "Dubai Hills Estate",
                "Arabian Ranches", "Palm Jumeirah", "Jumeirah", "Mirdif", "Al Nahda", "Deira", "Bur Dubai",
                "Dubai Silicon Oasis", "Motor City", "Discovery Gardens", "International City"],
      "body": [
        ("Cleaning towers, townhouses and villas",
         "<p>Most Dubai homes are high-rise apartments, where the team works with building security, service lifts and set working hours. In villa and townhouse communities the job is bigger: more bathrooms, terraces, maid's rooms and often a water tank on the roof. We plan the team size and time around the type of home you send us.</p>"),
        ("Building access in Dubai",
         "<p>Many towers and communities register service teams at the gate or ask for an access request from the resident. Tell us your building and the hours it allows, and register the team if needed, so the visit starts on time. For move-out cleaning, check whether your building needs a move permit on the same day.</p>"),
      ],
      "faqs": [
        ("Which areas of Dubai do you cover?", "We cover the main residential and business areas listed on this page. If yours isn't listed, send us the location on WhatsApp and we'll confirm."),
        ("Can you clean on weekends?", "Yes. Weekend slots fill up first, so it helps to book a few days ahead."),
        ("Do you clean holiday homes between guests?", "Yes. Send us your checkout and check-in times and we'll plan a turnaround clean in between."),
      ],
    },
    "ar": {
      "name": "دبي", "h1_short": "التنظيف في دبي",
      "title": "شركة تنظيف في دبي | تنظيف شقق وفلل ومكاتب | نقاء",
      "desc": "تنظيف منازل وتنظيف عميق وتنظيف بعد الإخلاء وكنب ومكاتب في دبي: المارينا وJVC وداون تاون والبرشاء وغيرها. السعر على واتساب قبل الحجز.",
      "h1": "شركة تنظيف في دبي",
      "lead": "شقق في الأبراج، وفلل في المجمعات السكنية، ومكاتب في مناطق الأعمال. فرقنا تغطي دبي من المارينا إلى مردف، والمواد والمعدات علينا.",
      "areas": ["دبي مارينا", "أبراج بحيرات جميرا JLT", "قرية جميرا الدائرية JVC", "داون تاون دبي", "الخليج التجاري",
                "البرشاء", "دبي هيلز", "المرابع العربية", "نخلة جميرا", "جميرا", "مردف", "النهدة", "ديرة",
                "بر دبي", "واحة دبي للسيليكون", "موتور سيتي", "ديسكفري جاردنز", "المدينة العالمية"],
      "body": [
        ("تنظيف الأبراج والتاون هاوس والفلل",
         "<p>أغلب بيوت دبي شقق في أبراج عالية، ويعمل الفريق فيها مع أمن المبنى ومصاعد الخدمة وساعات العمل المحددة. أما في مجمعات الفلل والتاون هاوس فالعمل أكبر: حمامات أكثر، وتراسات، وغرف خدم، وغالبًا خزان مياه على السطح. نحدد حجم الفريق والوقت حسب نوع البيت الذي ترسله لنا.</p>"),
        ("الدخول إلى المباني في دبي",
         "<p>كثير من الأبراج والمجمعات تسجّل فرق الخدمة عند البوابة أو تطلب طلب دخول من الساكن. أخبرنا باسم المبنى والساعات المسموح بها، وسجّل الفريق إذا لزم الأمر، لتبدأ الزيارة في وقتها. وفي التنظيف بعد الإخلاء تأكد إن كان المبنى يطلب تصريح انتقال في نفس اليوم.</p>"),
      ],
      "faqs": [
        ("ما المناطق التي تغطونها في دبي؟", "نغطي المناطق السكنية والتجارية الرئيسية المذكورة في هذه الصفحة. وإذا لم تجد منطقتك أرسل لنا الموقع على واتساب ونؤكد لك."),
        ("هل تنظفون في نهاية الأسبوع؟", "نعم. مواعيد نهاية الأسبوع تُحجز أولًا، لذلك يُفضّل الحجز قبلها بأيام."),
        ("هل تنظفون بيوت العطلات بين الضيوف؟", "نعم. أرسل لنا موعدي المغادرة والوصول ونرتب تنظيفًا سريعًا بينهما."),
      ],
    },
  },
  {
    "slug": "abu-dhabi",
    "en": {
      "name": "Abu Dhabi", "h1_short": "Cleaning in Abu Dhabi",
      "title": "Cleaning Company in Abu Dhabi | Homes & Villas | Naqaa",
      "desc": "Home, deep, move-in/move-out, sofa, water tank and office cleaning in Abu Dhabi: Al Reem, Khalifa City, Yas, Saadiyat and more.",
      "h1": "Cleaning company in Abu Dhabi",
      "lead": "From island apartments on Al Reem and Yas to family villas in Khalifa City and Mohammed Bin Zayed City, we bring a trained team and our own equipment to your door.",
      "areas": ["Al Reem Island", "Yas Island", "Saadiyat Island", "Al Raha Beach", "Khalifa City",
                "Mohammed Bin Zayed City", "Al Reef", "Masdar City", "Corniche", "Al Khalidiyah",
                "Al Mushrif", "Shakhbout City"],
      "body": [
        ("Villas and family homes",
         "<p>A large share of Abu Dhabi's homes are villas with several bedrooms, a majlis and outdoor areas. These homes benefit from a <a href=\"/services/deep-cleaning/\">deep clean</a> a few times a year and regular cleaning in between. Many also have their own water tank, which we can clean in the same visit.</p>"),
        ("Island apartments",
         "<p>On Al Reem, Yas and Saadiyat, apartments face the sea and collect salt and dust on balconies and glass. We include balcony and sliding-door tracks in every home clean, and full window cleaning from the inside in deep cleans.</p>"),
      ],
      "faqs": [
        ("Do you cover the mainland and the islands?", "Yes. We cover the areas listed on this page. Send us your location if you're not sure."),
        ("Can you clean a villa and its water tank on the same day?", "Yes. Tell us both when you ask for a price and we'll send a team for each."),
        ("Do you clean majlis seating?", "Yes, as part of our sofa and carpet cleaning service."),
      ],
    },
    "ar": {
      "name": "أبوظبي", "h1_short": "التنظيف في أبوظبي",
      "title": "شركة تنظيف في أبوظبي | تنظيف منازل وفلل | نقاء",
      "desc": "تنظيف منازل وتنظيف عميق وقبل السكن وبعد الإخلاء وكنب وخزانات ومكاتب في أبوظبي: جزيرة الريم ومدينة خليفة وياس والسعديات وغيرها.",
      "h1": "شركة تنظيف في أبوظبي",
      "lead": "من شقق جزيرة الريم وياس إلى فلل العائلات في مدينة خليفة ومدينة محمد بن زايد، نصلك بفريق مدرّب ومعداتنا الخاصة.",
      "areas": ["جزيرة الريم", "جزيرة ياس", "جزيرة السعديات", "شاطئ الراحة", "مدينة خليفة",
                "مدينة محمد بن زايد", "الريف", "مدينة مصدر", "الكورنيش", "الخالدية", "المشرف", "مدينة شخبوط"],
      "body": [
        ("الفلل وبيوت العائلات",
         "<p>جزء كبير من بيوت أبوظبي فلل بعدة غرف نوم ومجلس ومساحات خارجية. هذه البيوت تستفيد من <a href=\"/ar/services/deep-cleaning/\">تنظيف عميق</a> عدة مرات في السنة وتنظيف دوري بينها. وكثير منها لديه خزان مياه خاص يمكننا تنظيفه في نفس الزيارة.</p>"),
        ("شقق الجزر",
         "<p>في الريم وياس والسعديات تطل الشقق على البحر وتتجمع الأملاح والغبار على البلكونات والزجاج. نضيف البلكونة ومجاري الأبواب المنزلقة في كل تنظيف منزلي، وتنظيف النوافذ بالكامل من الداخل في التنظيف العميق.</p>"),
      ],
      "faqs": [
        ("هل تغطون البر الرئيسي والجزر؟", "نعم. نغطي المناطق المذكورة في هذه الصفحة. أرسل لنا موقعك إذا لم تكن متأكدًا."),
        ("هل يمكن تنظيف الفيلا وخزانها في نفس اليوم؟", "نعم. أخبرنا بالخدمتين عند طلب السعر ونرسل فريقًا لكل منهما."),
        ("هل تنظفون جلسات المجالس؟", "نعم، ضمن خدمة تنظيف الكنب والسجاد."),
      ],
    },
  },
  {
    "slug": "sharjah",
    "en": {
      "name": "Sharjah", "h1_short": "Cleaning in Sharjah",
      "title": "Cleaning Company in Sharjah | Home & Deep Cleaning | Naqaa",
      "desc": "Home, deep, move-out, sofa, water tank and office cleaning in Sharjah: Al Majaz, Al Nahda, Al Taawun, Muwaileh, Aljada and more.",
      "h1": "Cleaning company in Sharjah",
      "lead": "Family apartments on Al Majaz and Al Taawun, new communities in Aljada and Al Zahia, and villas across the city. One team, one clear price, booked on WhatsApp.",
      "areas": ["Al Majaz", "Al Nahda", "Al Taawun", "Al Khan", "Al Qasimia", "Muwaileh",
                "University City", "Aljada", "Al Zahia", "Al Mamzar"],
      "body": [
        ("Family apartments and new communities",
         "<p>Sharjah has many larger family apartments, where kitchens and bathrooms get heavy daily use. A <a href=\"/services/deep-cleaning/\">deep clean</a> followed by regular visits keeps them manageable. In newer communities like Aljada and Al Zahia, we often do move-in cleans to remove handover dust before families settle in.</p>"),
        ("Living between Sharjah and Dubai",
         "<p>Many Sharjah residents work in Dubai and leave early. You don't have to wait at home: let us know how the team can get access, and we'll send you photos when the job is done.</p>"),
      ],
      "faqs": [
        ("Which areas of Sharjah do you cover?", "The areas listed on this page. Send your location if you're not sure."),
        ("Can you clean while I'm at work?", "Yes, if you arrange access with building security or leave a key. We send photos when the job is done."),
        ("Do you clean villa water tanks in Sharjah?", "Yes. Send us the tank's location and a photo of the access."),
      ],
    },
    "ar": {
      "name": "الشارقة", "h1_short": "التنظيف في الشارقة",
      "title": "شركة تنظيف في الشارقة | تنظيف منازل وتنظيف عميق | نقاء",
      "desc": "تنظيف منازل وتنظيف عميق وبعد الإخلاء وكنب وخزانات ومكاتب في الشارقة: المجاز والنهدة والتعاون ومويلح والجادة وغيرها.",
      "h1": "شركة تنظيف في الشارقة",
      "lead": "شقق العائلات في المجاز والتعاون، والمجتمعات الجديدة في الجادة والزاهية، والفلل في أنحاء المدينة. فريق واحد وسعر واضح، والحجز على واتساب.",
      "areas": ["المجاز", "النهدة", "التعاون", "الخان", "القاسمية", "مويلح", "المدينة الجامعية", "الجادة", "الزاهية", "الممزر"],
      "body": [
        ("شقق العائلات والمجتمعات الجديدة",
         "<p>في الشارقة كثير من شقق العائلات الكبيرة، حيث يُستخدم المطبخ والحمامات بكثافة يوميًا. <a href=\"/ar/services/deep-cleaning/\">التنظيف العميق</a> ثم الزيارات الدورية يجعلانها أسهل في المتابعة. وفي المجتمعات الأحدث مثل الجادة والزاهية نقوم غالبًا بتنظيف قبل السكن لإزالة غبار التسليم قبل انتقال العائلة.</p>"),
        ("بين الشارقة ودبي",
         "<p>كثير من سكان الشارقة يعملون في دبي ويخرجون مبكرًا. لا تحتاج الانتظار في البيت: أخبرنا كيف يدخل الفريق، ونرسل لك صورًا عند انتهاء العمل.</p>"),
      ],
      "faqs": [
        ("ما المناطق التي تغطونها في الشارقة؟", "المناطق المذكورة في هذه الصفحة. أرسل موقعك إذا لم تكن متأكدًا."),
        ("هل يمكن التنظيف وأنا في العمل؟", "نعم، إذا رتبت الدخول مع أمن المبنى أو تركت مفتاحًا. نرسل لك صورًا عند انتهاء العمل."),
        ("هل تنظفون خزانات الفلل في الشارقة؟", "نعم. أرسل لنا مكان الخزان وصورة لمكان الوصول إليه."),
      ],
    },
  },
  {
    "slug": "ajman",
    "en": {
      "name": "Ajman", "h1_short": "Cleaning in Ajman",
      "title": "Cleaning Company in Ajman | Homes & Offices | Naqaa",
      "desc": "Home, deep, move-in/move-out, sofa, water tank and office cleaning in Ajman: Al Nuaimiya, Al Rashidiya, Al Jurf, Al Yasmeen and more.",
      "h1": "Cleaning company in Ajman",
      "lead": "Apartments along the Corniche and in Al Nuaimiya, and villas in Al Yasmeen, Al Mowaihat and Al Jurf. Trained cleaners and a clear price before we arrive.",
      "areas": ["Al Nuaimiya", "Al Rashidiya", "Al Jurf", "Ajman Corniche", "Al Rawda", "Al Mowaihat", "Al Yasmeen", "Emirates City"],
      "body": [
        ("Apartments and villas in Ajman",
         "<p>Ajman mixes high-rise apartments near the Corniche with growing villa areas inland. Apartments usually need regular cleaning and the occasional <a href=\"/services/sofa-carpet-cleaning/\">sofa clean</a>; villas often add a deep clean and a <a href=\"/services/water-tank-cleaning/\">water tank clean</a>.</p>"),
        ("Booking from Ajman",
         "<p>Send us your area and building on WhatsApp. We'll confirm the price, the team size and the earliest time we can reach you.</p>"),
      ],
      "faqs": [
        ("Which areas of Ajman do you cover?", "The areas listed on this page. Send your location if you're not sure."),
        ("Do you clean small offices and shops in Ajman?", "Yes. See our office cleaning service for what's included."),
        ("Can I book one-off cleaning?", "Yes. You can book a single visit or set a regular schedule."),
      ],
    },
    "ar": {
      "name": "عجمان", "h1_short": "التنظيف في عجمان",
      "title": "شركة تنظيف في عجمان | تنظيف منازل وفلل ومكاتب | نقاء",
      "desc": "تنظيف منازل وتنظيف عميق وقبل السكن وبعد الإخلاء وكنب وخزانات ومكاتب في عجمان: النعيمية والراشدية والجرف والياسمين وغيرها.",
      "h1": "شركة تنظيف في عجمان",
      "lead": "شقق على الكورنيش وفي النعيمية، وفلل في الياسمين والمويهات والجرف. عمالة مدرّبة وسعر واضح قبل وصولنا.",
      "areas": ["النعيمية", "الراشدية", "الجرف", "كورنيش عجمان", "الروضة", "المويهات", "الياسمين", "مدينة الإمارات"],
      "body": [
        ("الشقق والفلل في عجمان",
         "<p>تجمع عجمان بين الأبراج السكنية قرب الكورنيش ومناطق فلل تتوسع في الداخل. الشقق تحتاج غالبًا تنظيفًا دوريًا و<a href=\"/ar/services/sofa-carpet-cleaning/\">تنظيف كنب</a> من حين لآخر، والفلل تضيف عادةً تنظيفًا عميقًا و<a href=\"/ar/services/water-tank-cleaning/\">تنظيف الخزان</a>.</p>"),
        ("الحجز من عجمان",
         "<p>أرسل لنا منطقتك واسم المبنى على واتساب، ونؤكد لك السعر وحجم الفريق وأقرب موعد نصل فيه.</p>"),
      ],
      "faqs": [
        ("ما المناطق التي تغطونها في عجمان؟", "المناطق المذكورة في هذه الصفحة. أرسل موقعك إذا لم تكن متأكدًا."),
        ("هل تنظفون المكاتب والمحلات الصغيرة في عجمان؟", "نعم. راجع خدمة تنظيف المكاتب لمعرفة ما تشمله."),
        ("هل يمكن حجز تنظيف لمرة واحدة؟", "نعم. يمكنك حجز زيارة واحدة أو تحديد جدول دوري."),
      ],
    },
  },
]
