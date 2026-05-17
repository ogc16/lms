import re
from .models import Lesson

KNOWLEDGE_BASE = {
    'python': (
        'Python remains one of the most popular languages in 2026, powering everything from '
        'AI/ML pipelines at Google and Meta to data analysis in financial institutions like JPMorgan. '
        'PEP 8 style guidelines and type hints (introduced in Python 3.5+) are now standard industry practice. '
        'The 2024 Python Developers Survey showed 87% of professional developers use Python for data science and 65% for web development.'
    ),
    'javascript': (
        'JavaScript continues to dominate web development in 2026. The ECMAScript 2025 specification '
        'introduced new features like `Set` methods and RegExp modifiers. Frameworks like React 19, '
        'Next.js 15, and the rising popularity of Bun runtime (2024–2025) have reshaped the ecosystem. '
        'According to the 2025 Stack Overflow survey, JavaScript remains the most commonly used language at 65%.'
    ),
    'react': (
        'React 19, released in late 2024, introduced the long-awaited compiler (React Forget) for automatic '
        'memoization. Server Components, introduced in Next.js 13 (2022) and now standard in 2026, '
        'represent a paradigm shift in how we build web applications. Over 42% of professional developers '
        'use React, making it the dominant frontend framework as of 2026.'
    ),
    'database': (
        'Modern database landscape in 2026 is multi-model. PostgreSQL 17 (released 2024) continues to gain '
        'market share with improved performance and JSON capabilities. Vector databases like Pinecone and pgvector '
        'have become essential for AI/ML applications. The rise of serverless databases like Neon and PlanetScale '
        '(2023–2026) has changed how developers approach data persistence.'
    ),
    'sql': (
        'SQL remains the unchallenged language for data manipulation. SQL:2023 standard introduced new '
        'properties like "property graphs" for graph database queries. In 2026, DuckDB has gained significant '
        'traction for analytical workloads, while SQLite (the world\'s most deployed database engine) powers '
        'billions of devices globally.'
    ),
    'network': (
        'Networking in 2026 is dominated by cloud-native architectures. IPv6 adoption reached 50% globally '
        'by early 2025. Software-Defined Networking (SDN) and Network Function Virtualization (NFV) are '
        'now standard in enterprise environments. The rise of eBPF (since 2020) has revolutionised network '
        'observability and security in Linux-based systems.'
    ),
    'security': (
        'Cybersecurity spending exceeded $300 billion globally in 2025. Zero-Trust Architecture (ZTA), '
        'mandated for US federal agencies since 2021, is now industry standard. Ransomware attacks cost '
        'businesses over $20 billion in 2024. AI-powered security tools and the rise of quantum-safe '
        'cryptography (NIST standards finalised 2024) define the current security landscape.'
    ),
    'cloud': (
        'Cloud computing market reached $700 billion in 2025. AWS, Azure, and GCP continue to dominate, '
        'but multi-cloud and edge computing are now the norm. Serverless architectures (AWS Lambda, '
        'Cloudflare Workers) and container orchestration (Kubernetes, adopted by 96% of organisations '
        'as of 2025) define modern infrastructure.'
    ),
    'machine learning': (
        'AI/ML in 2026 is experiencing a golden age driven by large language models. GPT-4o, Claude 3.5, '
        'Gemini 2.0, and open-weight models like Llama 3 and Mistral have democratised AI. The AI '
        'market exceeded $500 billion in 2025. MLOps (MLflow, Kubeflow) and responsible AI frameworks '
        'are now standard practice in enterprises deploying ML at scale.'
    ),
    'data science': (
        'Data science in 2026 is deeply integrated into every industry. The "data mesh" architecture pattern '
        '(introduced 2020) is widely adopted. Python remains the lingua franca, with Polars gaining on Pandas '
        'for performance. Generative AI has created new roles like "AI prompt engineer" and "LLM ops engineer."'
    ),
    'mobile': (
        'Mobile development in 2026 is dominated by cross-platform frameworks. React Native and Flutter '
        'power the majority of new apps. iOS 20 and Android 17 introduced advanced AI integration at the OS '
        'level. The mobile app market generated over $600 billion in revenue in 2025.'
    ),
    'docker': (
        'Docker and containers have become the universal packaging format. Docker Desktop alternatives '
        '(Rancher Desktop, Podman, Finch) gained traction after licensing changes in 2021. By 2026, '
        'OCI-compliant containers are used by 90% of enterprises. Multi-stage builds and distroless images '
        'are best practices for production deployments.'
    ),
    'kubernetes': (
        'Kubernetes (K8s) is the standard container orchestration platform, with a 96% adoption rate '
        'among enterprises in 2025. K8s 1.30 (2024) introduced new stability features. Managed Kubernetes '
        'services (EKS, AKS, GKE) dominate, and ecosystem tools like Helm, ArgoCD, and Istio are '
        'essential components of the cloud-native stack.'
    ),
    'devops': (
        'DevOps practices in 2026 emphasise platform engineering and Internal Developer Platforms (IDPs). '
        'GitOps (pioneered by Weaveworks ~2017) is now the standard deployment methodology. AI-assisted '
        'DevOps tools (GitHub Copilot for infrastructure, AI-driven incident response) are transforming '
        'the field. The "You Build It, You Run It" philosophy is universally adopted.'
    ),
    'agile': (
        'Agile methodologies have evolved significantly by 2026. While Scrum remains popular (used by ~60% '
        'of teams), hybrid approaches combining Agile with Waterfall elements are common. The Agile 2.0 '
        'movement emphasises outcomes over outputs. AI-assisted sprint planning and retro tools are '
        'increasingly used by modern teams.'
    ),
    'software testing': (
        'Software testing in 2026 is increasingly automated and AI-driven. Playwright has overtaken '
        'Selenium as the leading browser automation tool (2024 onwards). Shift-left testing and continuous '
        'testing in CI/CD pipelines are standard. AI-powered test generation tools can now create unit tests '
        'automatically from production code.'
    ),
    'html': (
        'HTML5, now over a decade old, continues to evolve. The latest WHATWG specification (2025) '
        'includes improved form controls, the `<dialog>` element for modals, and declarative shadow DOM. '
        'Web Components have gained mainstream adoption, and all modern browsers support the full HTML5 '
        'specification. Accessibility (WCAG 2.2, finalised 2023) is now a legal requirement in many jurisdictions.'
    ),
    'css': (
        'CSS in 2026 has never been more powerful. CSS Container Queries (2023), CSS Nesting (2024), '
        'and the `:has()` selector revolutionised responsive design. Tailwind CSS 4 (released 2025) '
        'uses the new CSS `@layer` and `@property` rules. CSS Grid and Subgrid are universally supported. '
        'The new CSS Color Level 4 functions (`oklch()`, `oklab()`) give designers more control over colour spaces.'
    ),
    'business': (
        'Modern business landscape in 2026 is shaped by AI transformation, ESG (Environmental, Social, Governance) '
        'requirements, and hybrid work models. Remote-first companies grew 40% between 2020 and 2025. '
        'Digital transformation spending reached $3.4 trillion in 2025. Business analytics and data-driven '
        'decision-making are now foundational skills for all managers.'
    ),
    'marketing': (
        'Marketing in 2026 is dominated by AI-powered personalisation, programmatic advertising (now 90% of '
        'digital ad spend), and privacy-first approaches following the deprecation of third-party cookies '
        '(Google Chrome phasing them out in 2024–2025). TikTok and short-form video continue to dominate '
        'social media marketing, while AI-generated content is both a tool and a challenge for marketers.'
    ),
    'accounting': (
        'Accounting in 2026 has been transformed by AI automation of routine tasks. IFRS 18 (effective 2024) '
        'replaced IAS 1 for presentation of financial statements. ESG reporting standards (ISSB S1 and S2, '
        'effective 2024) are now mandatory for many jurisdictions. Cloud accounting platforms like Xero '
        'and QuickBooks Online dominate the SMB market.'
    ),
    'economics': (
        'The global economy in 2025–2026 has been shaped by post-pandemic recovery, persistent inflation '
        '(central banks maintaining higher-for-longer rates), and the economic impact of AI adoption. '
        'GDP growth in emerging markets (especially India and Southeast Asia) outpaces developed economies. '
        'Cryptocurrency regulation frameworks were established in major economies during 2024–2025.'
    ),
    'entrepreneurship': (
        'Entrepreneurship in 2026 is thriving. Global startup funding rebounded to $400 billion in 2025 '
        'after the 2022–2023 downturn. AI-native startups attracted the most venture capital. The rise of '
        'no-code/low-code platforms has lowered barriers to entry. Remote-first and distributed team '
        'models are the default for new ventures.'
    ),
    'project management': (
        'Project management in 2026 is increasingly data-driven and AI-assisted. Tools like Jira, '
        'Asana, and Linear now include AI features for task estimation, risk prediction, and resource '
        'allocation. The Project Management Institute (PMI) updated the PMBOK Guide in 2024 to include '
        'hybrid methodologies and AI in project management as core knowledge areas.'
    ),
    'leadership': (
        'Leadership in 2026 emphasises emotional intelligence, remote team management, and AI literacy. '
        'The shift to hybrid and remote work forced a fundamental rethinking of management practices. '
        'Research from McKinsey (2024) shows that organisations with inclusive leadership outperform '
        'peers by 35%. Leading through uncertainty and change remains the defining challenge for modern leaders.'
    ),
    'hr': (
        'Human Resources in 2026 leverages AI for recruitment screening, performance management, and '
        'employee engagement analytics. The "Great Resignation" (2021–2023) evolved into the "Great '
        'Reshuffle" by 2025, with employees prioritising flexibility and purpose. DEI (Diversity, Equity, '
        'and Inclusion) initiatives are now standard corporate practice, with many jurisdictions mandating '
        'pay transparency and ESG reporting.'
    ),
}

FALLBACK = (
    'That\'s a great question about this topic. In the context of today\'s rapidly evolving landscape, '
    'it\'s important to consider both the foundational principles and the latest developments. '
    'I recommend reviewing the key concepts covered in this lesson, and then exploring how they apply '
    'to real-world scenarios. Would you like me to elaborate on any specific aspect?'
)


def get_topics(text: str) -> list[str]:
    text = text.lower()
    matched = []
    for keyword in KNOWLEDGE_BASE:
        if keyword in text:
            matched.append(keyword)
    return matched


def generate_response(lesson: Lesson, question: str) -> dict:
    all_text = f'{lesson.title} {lesson.description} {lesson.module.title} {lesson.module.learning_path.title}'
    topics = get_topics(all_text)

    intro_template = (
        f'I see you\'re studying **{lesson.module.learning_path.title}**, '
        f'specifically the lesson on **{lesson.title}**. '
        f'Let me help you understand this better.\n\n'
    )

    question_lower = question.lower()

    if any(re.search(r'\b' + re.escape(g) + r'\b', question_lower) for g in ['hi', 'hello', 'hey', 'good morning', 'good afternoon']):
        return {
            'answer': (
                f'Hello! Welcome to **{lesson.title}**. I\'m your AI instructor, here to help you '
                f'understand the material. Feel free to ask me anything about this lesson, '
                f'current industry practices, or real-world applications. What would you like to know?'
            )
        }

    if 'example' in question_lower or 'real-world' in question_lower or 'practical' in question_lower:
        if topics:
            kb = '\n\n'.join(KNOWLEDGE_BASE[t] for t in topics[:2])
            return {
                'answer': (
                    f'{intro_template}Great question about real-world applications!\n\n'
                    f'{kb}\n\n'
                    f'Would you like me to dive deeper into any specific aspect of this?'
                )
            }

    if 'why' in question_lower or 'important' in question_lower or 'relevant' in question_lower:
        rejoin = f'"In today\'s world, {lesson.title} is more relevant than ever"'
        if topics:
            kb = KNOWLEDGE_BASE[topics[0]]
            return {
                'answer': (
                    f'{intro_template}Excellent question about why this matters!\n\n'
                    f'{rejoin}. {kb}\n\n'
                    f'The core concepts in this lesson form the foundation for understanding '
                    f'how modern systems and practices work.'
                )
            }

    if 'explain' in question_lower or 'what is' in question_lower or 'how does' in question_lower:
        explanation = f'Let me break this down clearly.\n\n'
        if topics:
            explanation += (
                f'The concepts covered in **{lesson.title}** are fundamental to '
                f'{lesson.module.learning_path.title}. Here\'s how they connect to current industry practice:\n\n'
                f'{KNOWLEDGE_BASE[topics[0]]}\n\n'
                f'In practice, understanding these principles allows professionals to '
                f'build more robust, scalable, and maintainable systems.'
            )
        else:
            explanation += FALLBACK
        return {
            'answer': f'{intro_template}{explanation}'
        }

    if topics:
        kb_parts = [KNOWLEDGE_BASE[t] for t in topics[:3]]
        return {
            'answer': (
                f'{intro_template}'
                f'Here\'s some context from the current industry landscape that relates to your question:\n\n'
                + '\n\n'.join(kb_parts) +
                '\n\nIs there anything specific you\'d like me to elaborate on?'
            )
        }

    return {
        'answer': (
            f'{intro_template}'
            f'{FALLBACK}'
        )
    }
