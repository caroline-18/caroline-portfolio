from django.shortcuts import render
import pandas as pd
from django.core.paginator import Paginator

def home(request):

    jobs_df = pd.read_csv(
        "data/processed/jobs_clean.csv"
    )

    jobs_df["posted_date"] = pd.to_datetime(
        jobs_df["posted_date"]
    )

    skill_df = pd.read_csv(
        "data/processed/skill_summary.csv"
    )

    city_df = pd.read_csv(
        "data/processed/city_summary.csv"
    )

    company_df = pd.read_csv(
        "data/processed/company_summary.csv"
    )

    context = {

        "total_jobs": len(jobs_df),
        "total_skills": len(skill_df),
        "total_cities": len(city_df),
        "total_companies": len(company_df),

        "top_skills": skill_df.head(5).to_dict("records"),
        "top_cities": city_df.head(5).to_dict("records"),
        "top_companies": company_df.head(5).to_dict("records"),

        "skill_labels":
            skill_df.head(5)["skill"].tolist(),

        "skill_counts":
            skill_df.head(5)["count"].tolist(),

        "city_labels":
            city_df.head(5)["city"].tolist(),

        "city_counts":
            city_df.head(5)["count"].tolist(),

        "company_labels":
            company_df.head(5)["company"].tolist(),

        "company_counts":
            company_df.head(5)["count"].tolist(),
    }

    return render(
        request,
        "talent/index.html",
        context
    )

def jobs(request):

    jobs_df = pd.read_csv(
        "data/processed/jobs_clean.csv"
    )

    jobs_df["posted_date"] = pd.to_datetime(
        jobs_df["posted_date"]
    )

    # Filters

    search = request.GET.get("search", "")
    company = request.GET.get("company", "")
    city = request.GET.get("city", "")
    sort = request.GET.get("sort", "")


    # Search

    if search:
        jobs_df = jobs_df[
            jobs_df["title"].str.contains(search, case=False, na=False)
            |
            jobs_df["company"].str.contains(search, case=False, na=False)
        ]

    # Company Filter

    if company:
        jobs_df = jobs_df[
            jobs_df["company"] == company
        ]

    # City Filter

    if city:
        jobs_df = jobs_df[
            jobs_df["city"] == city
        ]

    # Sorting

    if sort == "company":
        jobs_df = jobs_df.sort_values("company")

    elif sort == "city":
        jobs_df = jobs_df.sort_values("city")

    elif sort == "newest":

        jobs_df = jobs_df.sort_values(
            by="posted_date",
            ascending=False
        )

    # Dropdown values

    companies = sorted(
        jobs_df["company"]
        .dropna()
        .unique()
        .tolist()
    )

    cities = sorted(
        jobs_df["city"]
        .fillna("Unknown")
        .unique()
        .tolist()
    )

    # Pagination

    paginator = Paginator(
        jobs_df.to_dict("records"),
        10
    )

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,

        "companies": companies,
        "cities": cities,

        "selected_search": search,
        "selected_company": company,
        "selected_city": city,
        "selected_sort": sort,
    }

    return render(
        request,
        "talent/jobs.html",
        context
    )

def job_detail(request, job_id):

    jobs_df = pd.read_csv(
        "data/processed/jobs_clean.csv"
    )

    skills_df = pd.read_csv(
        "data/processed/job_skills.csv"
    )

    job = jobs_df[
        jobs_df["job_id"].astype(str) == str(job_id)
    ]

    if job.empty:
        return render(
            request,
            "talent/not_found.html"
        )

    job = job.iloc[0]
    job["posted_date"] = pd.to_datetime(
    job["posted_date"]
    ).strftime("%d %b %Y")

    skills = skills_df[
        skills_df["job_id"].astype(str) == str(job_id)
    ]["skill"].tolist()

    context = {
        "job": job,
        "skills": skills,
    }

    return render(
        request,
        "talent/job_detail.html",
        context
    )

def skills(request):

    skills_df = pd.read_csv(
        "data/processed/skill_summary.csv"
    )

    search = request.GET.get("search", "")
    sort = request.GET.get("sort", "")

    # Search

    if search:
        skills_df = skills_df[
            skills_df["skill"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

    # Sorting

    if sort == "skill":
        skills_df = skills_df.sort_values(
            by="skill"
        )

    elif sort == "count":
        skills_df = skills_df.sort_values(
            by="count",
            ascending=False
        )

    # Pagination

    paginator = Paginator(
        skills_df.to_dict("records"),
        10
    )

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "selected_search": search,
        "selected_sort": sort,
    }

    return render(
        request,
        "talent/skills.html",
        context
    )

def companies(request):

    company_df = pd.read_csv(
        "data/processed/company_summary.csv"
    )

    search = request.GET.get("search", "")
    sort = request.GET.get("sort", "")

    # Search

    if search:
        company_df = company_df[
            company_df["company"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

    # Sorting

    if sort == "company":
        company_df = company_df.sort_values(
            by="company"
        )

    elif sort == "count":
        company_df = company_df.sort_values(
            by="count",
            ascending=False
        )

    # Pagination

    paginator = Paginator(
        company_df.to_dict("records"),
        10
    )

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "selected_search": search,
        "selected_sort": sort,
    }

    return render(
        request,
        "talent/companies.html",
        context
    )

def cities(request):

    city_df = pd.read_csv(
        "data/processed/city_summary.csv"
    )

    search = request.GET.get("search", "")
    sort = request.GET.get("sort", "")

    # Search

    if search:
        city_df = city_df[
            city_df["city"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

    # Sorting

    if sort == "city":
        city_df = city_df.sort_values(
            by="city"
        )

    elif sort == "count":
        city_df = city_df.sort_values(
            by="count",
            ascending=False
        )

    # Pagination

    paginator = Paginator(
        city_df.to_dict("records"),
        10
    )

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "selected_search": search,
        "selected_sort": sort,
    }

    return render(
        request,
        "talent/cities.html",
        context
    )

def company_detail(request, company_name):

    jobs_df = pd.read_csv(
        "data/processed/jobs_clean.csv"
    )

    company_jobs = jobs_df[
        jobs_df["company"] == company_name
    ]

    if company_jobs.empty:
        return render(
            request,
            "talent/not_found.html"
        )

    city_summary = (
        company_jobs["city"]
        .value_counts()
        .reset_index()
    )

    city_summary.columns = [
        "city",
        "count"
    ]

    context = {
        "company": company_name,
        "total_jobs": len(company_jobs),
        "jobs": company_jobs.to_dict("records"),
        "cities": city_summary.to_dict("records"),
    }

    return render(
        request,
        "talent/company_detail.html",
        context
    )

def city_detail(request, city_name):

    jobs_df = pd.read_csv(
        "data/processed/jobs_clean.csv"
    )

    skills_df = pd.read_csv(
        "data/processed/job_skills.csv"
    )

    city_jobs = jobs_df[
        jobs_df["city"] == city_name
    ]

    if city_jobs.empty:

        return render(
            request,
            "talent/not_found.html"
        )

    company_summary = (
        city_jobs["company"]
        .value_counts()
        .head(5)
        .reset_index()
    )

    company_summary.columns = [
        "company",
        "count"
    ]

    city_job_ids = (
        city_jobs["job_id"]
        .astype(str)
        .tolist()
    )

    city_skills = skills_df[
        skills_df["job_id"]
        .astype(str)
        .isin(city_job_ids)
    ]

    skill_summary = (
        city_skills["skill"]
        .value_counts()
        .head(5)
        .reset_index()
    )

    skill_summary.columns = [
        "skill",
        "count"
    ]

    context = {

        "city": city_name,

        "total_jobs": len(city_jobs),

        "companies":
            company_summary.to_dict("records"),

        "skills":
            skill_summary.to_dict("records"),

        "jobs":
            city_jobs
            .head(10)
            .to_dict("records"),
    }

    return render(
        request,
        "talent/city_detail.html",
        context
    )


def company_detail(request, company_name):

    jobs_df = pd.read_csv(
        "data/processed/jobs_clean.csv"
    )

    company_jobs = jobs_df[
        jobs_df["company"] == company_name
    ]

    if company_jobs.empty:

        return render(
            request,
            "talent/not_found.html"
        )

    city_summary = (
        company_jobs["city"]
        .value_counts()
        .head(5)
        .reset_index()
    )

    city_summary.columns = [
        "city",
        "count"
    ]

    context = {

        "company": company_name,

        "total_jobs": len(
            company_jobs
        ),

        "cities":
            city_summary.to_dict(
                "records"
            ),

        "jobs":
            company_jobs
            .head(10)
            .to_dict(
                "records"
            )

    }

    return render(
        request,
        "talent/company_detail.html",
        context
    )

def skill_detail(request, skill_name):

    jobs_df = pd.read_csv(
        "data/processed/jobs_clean.csv"
    )

    skills_df = pd.read_csv(
        "data/processed/job_skills.csv"
    )

    skill_jobs = skills_df[
        skills_df["skill"] == skill_name
    ]

    if skill_jobs.empty:

        return render(
            request,
            "talent/not_found.html"
        )

    job_ids = skill_jobs[
        "job_id"
    ].astype(str).tolist()

    filtered_jobs = jobs_df[
        jobs_df["job_id"]
        .astype(str)
        .isin(job_ids)
    ]

    company_summary = (
        filtered_jobs["company"]
        .value_counts()
        .head(5)
        .reset_index()
    )

    company_summary.columns = [
        "company",
        "count"
    ]

    city_summary = (
        filtered_jobs["city"]
        .value_counts()
        .head(5)
        .reset_index()
    )

    city_summary.columns = [
        "city",
        "count"
    ]

    context = {

        "skill": skill_name,

        "total_jobs":
            len(filtered_jobs),

        "companies":
            company_summary.to_dict(
                "records"
            ),

        "cities":
            city_summary.to_dict(
                "records"
            ),

        "jobs":
            filtered_jobs
            .head(10)
            .to_dict(
                "records"
            )

    }

    return render(
        request,
        "talent/skill_detail.html",
        context
    )