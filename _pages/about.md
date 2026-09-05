---
permalink: /
title: ""
excerpt: ""
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---

{% if site.google_scholar_stats_use_cdn %}
{% assign gsDataBaseUrl = "https://cdn.jsdelivr.net/gh/" | append: site.repository | append: "@" %}
{% else %}
{% assign gsDataBaseUrl = "https://raw.githubusercontent.com/" | append: site.repository | append: "/" %}
{% endif %}
{% assign url = gsDataBaseUrl | append: "google-scholar-stats/gs_data_shieldsio.json" %}

<span class='anchor' id='about-me'></span>

Hi, my name is **Chunlin Gong (巩春林)**. I am currently a PhD student at the **University of Minnesota**, in the **Department of Computer Science and Engineering**, advised by [Prof. Mattia Fazzini](https://www-users.cse.umn.edu/~mfazzini/) and [Prof. Caiwen Ding](https://caiwending.github.io/).

My primary research interests lie in **trustworthy agentic systems**—building AI agents that are safe, reliable, and aligned with human values. I study how to ensure the security and robustness of LLM-based agents in open-ended environments, and explore alignment methods to make these systems more trustworthy in real-world deployment.

I also had the privilege of interning at the **Institute of Automation, Chinese Academy of Sciences (CASIA)** and **Shanghai AI Lab**. I am deeply grateful for the guidance and support from [Prof. Shu Wu](http://shuwu.name/), [Prof. Xingcheng Xu](https://xingchengxu.github.io/), and Prof. Zhao Tong.

<span class='anchor' id='news'></span>

# 🔥 News

- *2025.12*: &nbsp;🎉I joined the Shanghai AI Lab to conduct research on safety alignment strategies in collaboration with CASIA.
- *2025.08*: &nbsp;🎉I joined the software engineering research group at the University of Minnesota, to study safetyissues related to logs.
- *2025.05*: &nbsp;🎉 I joined the Institute of Automation, Chinese Academy of Sciences (CASIA), to research content Safety in social media.
- 2024.9: 🏠Thanks to Prof. Wang, School of Control Science and Engineering, Shandong University. Our project has been approved by the Shandong Provincial Natural Science Foundation! This will be the starting point for my research.

<span class='anchor' id='publications'></span>
# 📝 Publications (* Equal Contribution)

<div class="paper-box">
  <div class="paper-box-image">
    <div class="badge" style="background-color: #e74c3c;">ICML 2026</div>
    <img src="./images/CoT.png" alt="sym" style="width:500px;height:200px;object-fit:cover;">
  </div>

  <div class="paper-box-text">
    <p><a href="https://arxiv.org/pdf/2602.04856">
      <strong>CoT is Not the Chain of Truth: An Empirical Internal Analysis of Reasoning LLMs for Fake News Generation</strong>
    </a></p>


    <p>Zhao Tong*,<strong>Chunlin Gong*</strong>, Yiping Zhang, Haichao Shi, Qiang Liu, Xingcheng Xu, Shu Wu, Xiao-Yu Zhang</p>
    
    <ul>
      <li>Our paper shows that in fake-news generation, reasoning LLMs can still produce unsafe, deceptive content inside their chain-of-thought even when the final answer is a refusal, and proposes a layer/head-level Jacobian spectral analysis to localize the safety-critical routing mechanisms driving that divergence.</li>
    </ul>
  </div>
</div>



<div class="paper-box">
  <div class="paper-box-image">
    <div class="badge">EMNLP 2026 Main</div>
    <img src="./images/AdComment.png" alt="sym" width="500" height="300">
  </div>

  <div class="paper-box-text">
    <p><a href="https://arxiv.org/pdf/2510.09712?">
      <strong>Group-Adaptive Adversarial Learning for Robust Fake News Detection Against Malicious Comments</strong>
    </a></p>


    <p>Zhao Tong*, <strong>Chunlin Gong*</strong>, Yimeng Gu, Qiang Liu, Shu Wu, Haichao Shi, Xiao-Yu Zhang</p>
    
    <ul>
      <li>This paper demonstrates that fake-news detectors are highly vulnerable to psychological-based malicious adversarial comments and proposes group-adaptive adversarial training to substantially improve robustness.</li>
    </ul>
  </div>
</div>


<span class='anchor' id='honors-and-awards'></span>
# 🎖 Honors and Awards
- *2025* University of Minnesota UROP Scholarship💴
- *2024* Shandong Provincial Natural Science Foundation💴, Funded (Sole student member).
- *2023* National Bronze Medal🥉, The International Collegiate Programming Contest (ACM-ICPC).

- *2022* Second Prize🥈, Shandong Division, National Olympiad in Informatics(NOIP).

<span class='anchor' id='educations'></span>
# 📖 Educations
- 2026–Present, Ph.D. in Computer Science, University of Minnesota, Twin Cities.
- 2023–2026, B.A. in Computer Science, University of Minnesota, Twin Cities.
- 2020–2023, Shandong Experimental High School.

<span class='anchor' id='research-experience'></span>

# 💻 Research Experience

<div class="paper-box-mini" style="display:flex; gap:12px; align-items:flex-start;">
  <div class="left" style="flex:0 0 auto;">
    <img src="./images/AI_LAB.png" style="width:50px;height:30px;display:block;">
  </div>
  <div class="right" style="display:flex; flex-direction:column; gap:6px;">
    <div class="title" style="display:flex; align-items:center; gap:10px; flex-wrap:wrap; font-weight:600;">
      <span>LLM Research Intern · Shanghai AI Lab</span>
    </div>



    <p class="meta" style="margin:0; color:#555; font-size:13px; line-height:1.4;">
      December 2025 – May 2026 · Shanghai, China · Mentors: Prof. Xingcheng Xu.
    </p>
    
    <ul class="bullets" style="margin:0; padding-left:18px; line-height:1.5;">
      <li>Collaborate with CASIA to analyze and develop defense strategies for multimodal large-scale safety issues.</li>
    </ul>
  </div>
</div>

<br>

<div class="paper-box-mini" style="display:flex; gap:12px; align-items:flex-start;">
  <div class="left" style="flex:0 0 auto;">
    <img src="./images/UMN.jpeg" style="width:50px;height:30px;display:block;">
  </div>
  <div class="right" style="display:flex; flex-direction:column; gap:6px;">
    <div class="title" style="display:flex; align-items:center; gap:10px; flex-wrap:wrap; font-weight:600;">
      <span>Research Assistant · University of Minnesota</span>
    </div>



    <p class="meta" style="margin:0; color:#555; font-size:13px; line-height:1.4;">
      August 2025 – May 2026 · Minneapolis, United States · Mentors: Prof. Mattia Fazzini
    </p>
    
    <ul class="bullets" style="margin:0; padding-left:18px; line-height:1.5;">
      <li>Research on software engineering security focuses on anomaly detection in log files.</li>
    </ul>

  </div>
</div>

<br>

<div class="paper-box-mini" style="display:flex; gap:12px; align-items:flex-start;">
  <div class="left" style="flex:0 0 auto;">
    <img src="./images/CAS.jpg" style="width:50px;height:50px;display:block;">
  </div>
  <div class="right" style="display:flex; flex-direction:column; gap:6px;">
    <div class="title" style="display:flex; align-items:center; gap:10px; flex-wrap:wrap; font-weight:600;">
      <span>Algorithm Intern · Institution of Automation, Chinese academy of science</span>
    </div>



    <p class="meta" style="margin:0; color:#555; font-size:13px; line-height:1.4;">
      May 2025 – May 2026 · Beijing, China · Mentors: Prof. Shu Wu and Prof. Zhao Tong
    </p>
    
    <ul class="bullets" style="margin:0; padding-left:18px; line-height:1.5;">
      <li>Content Safety in social media and LLM safety</li>
    </ul>

  </div>
</div>

