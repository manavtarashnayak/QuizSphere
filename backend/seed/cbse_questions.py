"""Predefined question bank covering CBSE Class 11th & 12th subjects and Basic Programming."""

SEED_QUIZZES = [
    {
        "id": "cbse-phys-11-12",
        "title": "CBSE Physics (Classes 11 & 12)",
        "description": "Fundamental concepts from CBSE Class 11 & 12 Physics: Mechanics, Thermodynamics, Electrostatics, and Optics.",
        "category": "Physics",
        "difficulty": "Intermediate",
        "duration_minutes": 20,
        "passing_score_percentage": 50,
        "questions": [
            {
                "id": "phys_1",
                "text": "What is the dimensional formula of Universal Gravitational Constant (G)?",
                "options": ["[M⁻¹ L³ T⁻²]", "[M¹ L² T⁻²]", "[M⁻¹ L² T⁻¹]", "[M⁰ L³ T⁻²]"],
                "correct_option": 0,
                "explanation": "From F = G*m1*m2/r², G = F*r²/(m1*m2) -> [M L T⁻²][L²]/[M²] = [M⁻¹ L³ T⁻²]."
            },
            {
                "id": "phys_2",
                "text": "In projectile motion under gravity (ignoring air resistance), which component of velocity remains constant?",
                "options": ["Vertical component", "Horizontal component", "Both vertical and horizontal", "Neither"],
                "correct_option": 1,
                "explanation": "No external force acts along the horizontal axis, so horizontal velocity (u*cos(theta)) remains constant."
            },
            {
                "id": "phys_3",
                "text": "According to the First Law of Thermodynamics, ΔQ is equal to:",
                "options": ["ΔU - W", "ΔU + W", "W - ΔU", "ΔU * W"],
                "correct_option": 1,
                "explanation": "The first law of thermodynamics states ΔQ = ΔU + ΔW (heat supplied = increase in internal energy + work done)."
            },
            {
                "id": "phys_4",
                "text": "What is the electric field inside a charged thin spherical conducting shell of radius R?",
                "options": ["Zero", "q / (4πε₀ R²)", "q / (4πε₀ r)", "Infinite"],
                "correct_option": 0,
                "explanation": "By Gauss's Law, the enclosed charge inside a hollow conducting shell is zero, so the electrostatic field E = 0 inside."
            },
            {
                "id": "phys_5",
                "text": "Which phenomenon demonstrates the transverse wave nature of light?",
                "options": ["Interference", "Diffraction", "Polarization", "Refraction"],
                "correct_option": 2,
                "explanation": "Polarization can only occur in transverse waves where vibrations are perpendicular to wave propagation."
            },
            {
                "id": "phys_6",
                "text": "The SI unit of magnetic flux is:",
                "options": ["Tesla", "Weber", "Henry", "Gauss"],
                "correct_option": 1,
                "explanation": "Magnetic flux is measured in Weber (Wb), whereas magnetic flux density (B) is measured in Tesla (T)."
            },
            {
                "id": "phys_7",
                "text": "In Young's Double Slit Experiment, what happens to fringe width if the distance between slits is halved?",
                "options": ["Halved", "Doubled", "Remains unchanged", "Quadrupled"],
                "correct_option": 1,
                "explanation": "Fringe width β = λD/d. If slit separation d is halved, β becomes 2 * β (doubles)."
            },
            {
                "id": "phys_8",
                "text": "What is the de Broglie wavelength associated with an electron accelerated through potential difference V?",
                "options": ["12.27 / √V Å", "1.227 / √V Å", "122.7 / √V Å", "0.1227 / √V Å"],
                "correct_option": 0,
                "explanation": "For an electron, λ = h/√(2meV) ≈ 12.27 / √V Å (or 1.227 / √V nm)."
            }
        ]
    },
    {
        "id": "cbse-chem-11-12",
        "title": "CBSE Chemistry (Classes 11 & 12)",
        "description": "Essential questions covering Physical, Organic, and Inorganic Chemistry from the CBSE 11th & 12th curriculum.",
        "category": "Chemistry",
        "difficulty": "Intermediate",
        "duration_minutes": 20,
        "passing_score_percentage": 50,
        "questions": [
            {
                "id": "chem_1",
                "text": "What is the hybridization of carbon in ethane, ethene, and ethyne respectively?",
                "options": ["sp³, sp², sp", "sp, sp², sp³", "sp², sp³, sp", "sp³, sp, sp²"],
                "correct_option": 0,
                "explanation": "Single-bonded carbon in ethane is sp³, double-bonded in ethene is sp², and triple-bonded in ethyne is sp."
            },
            {
                "id": "chem_2",
                "text": "According to Le Chatelier's principle, an increase in pressure on the equilibrium N₂(g) + 3H₂(g) ⇌ 2NH₃(g) will:",
                "options": ["Shift forward (produce more NH₃)", "Shift backward", "Have no effect", "Stop the reaction"],
                "correct_option": 0,
                "explanation": "4 moles of gas reactant form 2 moles of gas product. Increasing pressure shifts equilibrium toward fewer gas moles (forward)."
            },
            {
                "id": "chem_3",
                "text": "What is the oxidation state of Chromium in K₂Cr₂O₇?",
                "options": ["+4", "+5", "+6", "+3"],
                "correct_option": 2,
                "explanation": "2(+1) + 2(Cr) + 7(-2) = 0 => 2 + 2(Cr) - 14 = 0 => 2(Cr) = 12 => Cr = +6."
            },
            {
                "id": "chem_4",
                "text": "Which reagent is used in the Lucas Test to distinguish primary, secondary, and tertiary alcohols?",
                "options": ["Anhydrous ZnCl₂ + conc. HCl", "Alkaline KMnO₄", "Br₂ in CCl₄", "Acidified K₂Cr₂O₇"],
                "correct_option": 0,
                "explanation": "Lucas reagent is an equimolar mixture of concentrated hydrochloric acid (conc. HCl) and anhydrous zinc chloride (ZnCl₂)."
            },
            {
                "id": "chem_5",
                "text": "What is the unit of rate constant for a first-order reaction?",
                "options": ["mol L⁻¹ s⁻¹", "L mol⁻¹ s⁻¹", "s⁻¹", "mol² L⁻² s⁻¹"],
                "correct_option": 2,
                "explanation": "For an n-th order reaction, unit is (mol/L)^(1-n) s⁻¹. For n = 1, it simplifies to s⁻¹."
            },
            {
                "id": "chem_6",
                "text": "Which compound does NOT undergo the Aldol Condensation reaction?",
                "options": ["Acetaldehyde", "Benzaldehyde", "Propanal", "Acetone"],
                "correct_option": 1,
                "explanation": "Aldol condensation requires at least one α-hydrogen atom. Benzaldehyde (C₆H₅CHO) has no α-hydrogen."
            },
            {
                "id": "chem_7",
                "text": "Lanthanoid contraction is primarily caused by:",
                "options": [
                    "Poor shielding effect of 4f electrons",
                    "Strong shielding effect of 4f electrons",
                    "Increase in nuclear charge alone",
                    "Presence of 5d electrons"
                ],
                "correct_option": 0,
                "explanation": "Due to the diffuse shape of 4f orbitals, they offer poor shielding against nuclear charge, pulling outer electrons closer."
            }
        ]
    },
    {
        "id": "cbse-math-11-12",
        "title": "CBSE Mathematics (Classes 11 & 12)",
        "description": "Calculus, Matrices, Probability, Vectors, and Algebra from CBSE Class 11 & 12 syllabus.",
        "category": "Mathematics",
        "difficulty": "Advanced",
        "duration_minutes": 25,
        "passing_score_percentage": 50,
        "questions": [
            {
                "id": "math_1",
                "text": "What is the derivative of e^(sin x) with respect to x?",
                "options": ["cos(x) * e^(sin x)", "-cos(x) * e^(sin x)", "sin(x) * e^(cos x)", "e^(cos x)"],
                "correct_option": 0,
                "explanation": "Using chain rule: d/dx[e^(sin x)] = e^(sin x) * d/dx(sin x) = cos(x) * e^(sin x)."
            },
            {
                "id": "math_2",
                "text": "What is the value of ∫₀^(π/2) sin²(x) dx?",
                "options": ["π/2", "π/4", "1", "0"],
                "correct_option": 1,
                "explanation": "∫₀^(π/2) sin²(x) dx = ∫₀^(π/2) (1 - cos 2x)/2 dx = [x/2 - sin(2x)/4]₀^(π/2) = π/4."
            },
            {
                "id": "math_3",
                "text": "If A is an invertible square matrix of order n, what is det(adj A)?",
                "options": ["(det A)^n", "(det A)^(n - 1)", "n * det A", "1 / det A"],
                "correct_option": 1,
                "explanation": "Standard theorem in matrix algebra: |adj A| = |A|^(n - 1)."
            },
            {
                "id": "math_4",
                "text": "If two events A and B are independent with P(A) = 0.3 and P(B) = 0.4, what is P(A ∩ B)?",
                "options": ["0.7", "0.12", "0.1", "0.58"],
                "correct_option": 1,
                "explanation": "For independent events, P(A ∩ B) = P(A) * P(B) = 0.3 * 0.4 = 0.12."
            },
            {
                "id": "math_5",
                "text": "What is the dot product of two mutually perpendicular non-zero vectors?",
                "options": ["1", "-1", "0", "Their magnitudes product"],
                "correct_option": 2,
                "explanation": "a · b = |a||b| cos(θ). For perpendicular vectors, θ = 90° and cos(90°) = 0, so a · b = 0."
            },
            {
                "id": "math_6",
                "text": "The number of subsets of a set having 5 elements is:",
                "options": ["10", "25", "32", "64"],
                "correct_option": 2,
                "explanation": "The power set of a set with n elements contains 2^n subsets. 2^5 = 32."
            },
            {
                "id": "math_7",
                "text": "What is the value of lim(x -> 0) [sin(x) / x]?",
                "options": ["0", "1", "Undefined", "Infinity"],
                "correct_option": 1,
                "explanation": "Standard calculus limit: lim(x -> 0) sin(x)/x = 1."
            }
        ]
    },
    {
        "id": "cbse-cs-prog-11-12",
        "title": "Basic Programming & Python (CBSE CS)",
        "description": "Python fundamentals, data structures, control flow, functions, and SQL based on CBSE Class 11-12 Computer Science.",
        "category": "Computer Science",
        "difficulty": "Beginner",
        "duration_minutes": 15,
        "passing_score_percentage": 50,
        "questions": [
            {
                "id": "prog_1",
                "text": "What is the output of: print(type([1, 2, 3])) in Python?",
                "options": ["<class 'tuple'>", "<class 'list'>", "<class 'array'>", "<class 'set'>"],
                "correct_option": 1,
                "explanation": "Square brackets define a list literal in Python."
            },
            {
                "id": "prog_2",
                "text": "Which of the following data types in Python is IMMUTABLE?",
                "options": ["List", "Dictionary", "Tuple", "Set"],
                "correct_option": 2,
                "explanation": "Tuples, integers, floats, strings, and frozensets are immutable in Python; lists, dicts, and sets are mutable."
            },
            {
                "id": "prog_3",
                "text": "What is the output of: print('Hello' * 3)?",
                "options": ["Hello Hello Hello", "Hello*3", "HelloHelloHello", "TypeError"],
                "correct_option": 2,
                "explanation": "In Python, multiplying a string by an integer repeats the string without adding spaces."
            },
            {
                "id": "prog_4",
                "text": "What is the result of expression: 2 ** 3 ** 2 in Python?",
                "options": ["64", "512", "36", "12"],
                "correct_option": 1,
                "explanation": "Exponentiation operator (**) evaluates right-to-left: 3 ** 2 = 9, then 2 ** 9 = 512."
            },
            {
                "id": "prog_5",
                "text": "Which keyword is used to define a function in Python?",
                "options": ["function", "def", "fun", "define"],
                "correct_option": 1,
                "explanation": "Python uses the `def` keyword followed by function name and parameters: `def my_func():`."
            },
            {
                "id": "prog_6",
                "text": "In SQL, which clause is used to filter records grouped by the GROUP BY clause?",
                "options": ["WHERE", "HAVING", "ORDER BY", "FILTER"],
                "correct_option": 1,
                "explanation": "WHERE filters rows before aggregation; HAVING filters aggregate groupings."
            },
            {
                "id": "prog_7",
                "text": "What does a Boolean expression evaluate to?",
                "options": ["Any numeric value", "True or False", "A string literal", "Null"],
                "correct_option": 1,
                "explanation": "Boolean expressions evaluate to one of two truth values: True or False."
            },
            {
                "id": "prog_8",
                "text": "What will `list(range(2, 10, 3))` produce in Python?",
                "options": ["[2, 5, 8]", "[2, 5, 8, 10]", "[3, 6, 9]", "[2, 3, 4]"],
                "correct_option": 0,
                "explanation": "range(start=2, stop=10, step=3) generates 2, 2+3=5, 5+3=8. 8+3=11 which is >= 10, so it stops."
            }
        ]
    }
]
