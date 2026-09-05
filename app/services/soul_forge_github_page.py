from pathlib import Path
def _sf_github_delivery_page():
    import os
    import re
    import streamlit as st

    from app.services.soul_forge_github_delivery import (
        GitHubDeliveryError,
        changed_files,
        commit,
        create_feature_branch,
        create_pull_request,
        create_repository,
        current_branch,
        delivery_manifest,
        github_user,
        list_repositories,
        make_feature_branch_name,
        parse_owner_repo,
        push_feature_branch,
        remote_url,
        stage_files,
        staged_files,
        validate_selected_files,
    )

    # Resolve repository root from this file.
    # Works in Google Colab and Streamlit Cloud.
    project_root = Path(__file__).resolve().parents[2]

    st.title("🚀 GitHub Delivery")

    st.caption(
        "SOUL FORGE → feature branch → Pull Request → qa → "
        "manual merge to main"
    )

    st.info(
        "SOUL FORGE will never directly push generated functionality "
        "to main or automatically merge a Pull Request."
    )

    # -------------------------------------------------------------------------
    # Session state
    # -------------------------------------------------------------------------

    defaults = {
        "sf_gh_token": "",
        "sf_gh_repos": [],
        "sf_gh_repo_mode": "Existing repository",
        "sf_gh_selected_repo": "",
        "sf_gh_created_repo": None,
        "sf_gh_validation": None,
        "sf_gh_pr": None,
        "sf_gh_delivery_manifest": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # -------------------------------------------------------------------------
    # GitHub authentication
    # -------------------------------------------------------------------------

    st.subheader("1. GitHub connection")

    env_token = (
        os.environ.get("GITHUB_TOKEN")
        or os.environ.get("GH_TOKEN")
        or ""
    )

    if env_token:
        st.success(
            "GitHub token detected from the current Colab environment."
        )

    token = st.text_input(
        "GitHub Personal Access Token",
        value=st.session_state.get("sf_gh_token") or env_token,
        type="password",
        help=(
            "Used only for this SOUL FORGE session. "
            "Do not save the token in the repository."
        ),
    )

    st.session_state.sf_gh_token = token

    if not token:
        st.warning(
            "Enter a GitHub token to enable repository selection "
            "and Pull Request creation."
        )
        return

    if st.button(
        "🔐 Verify GitHub",
        use_container_width=True,
    ):
        try:
            user = github_user(token)

            st.session_state.sf_gh_username = user.get(
                "login",
                "GitHub user",
            )

            st.success(
                f"Connected to GitHub as "
                f"**{st.session_state.sf_gh_username}**"
            )

            repos = list_repositories(token)

            st.session_state.sf_gh_repos = repos

            st.success(
                f"Loaded {len(repos)} repositories."
            )

        except Exception as exc:
            st.error(f"GitHub connection failed: {exc}")
            return

    if not st.session_state.get("sf_gh_username"):
        return

    # -------------------------------------------------------------------------
    # Repository selection
    # -------------------------------------------------------------------------

    st.divider()
    st.subheader("2. Repository")

    repo_mode = st.radio(
        "Repository source",
        [
            "Existing repository",
            "Create new repository",
        ],
        horizontal=True,
        key="sf_gh_repo_mode",
    )

    if repo_mode == "Existing repository":

        repos = st.session_state.get("sf_gh_repos", [])

        if not repos:
            st.warning(
                "No repositories loaded. Press 'Verify GitHub' again."
            )
            return

        repo_names = [
            f"{repo.get('full_name', '')}"
            for repo in repos
            if repo.get("full_name")
        ]

        selected = st.selectbox(
            "Select repository",
            repo_names,
            key="sf_gh_selected_repo",
        )

        selected_data = next(
            (
                repo
                for repo in repos
                if repo.get("full_name") == selected
            ),
            None,
        )

        if selected_data:
            visibility = (
                "Private"
                if selected_data.get("private")
                else "Public"
            )

            st.caption(
                f"{visibility} • "
                f"default branch: "
                f"{selected_data.get('default_branch', 'unknown')}"
            )

    else:

        new_name = st.text_input(
            "New repository name",
            placeholder="my-soul-forge-generated-project",
        )

        new_description = st.text_input(
            "Repository description",
            value="Code generated and delivered by SOUL FORGE.",
        )

        new_private = st.checkbox(
            "Private repository",
            value=True,
        )

        if st.button(
            "➕ Create GitHub Repository",
            use_container_width=True,
        ):
            if not new_name.strip():
                st.error("Repository name is required.")
                return

            try:
                created = create_repository(
                    token=token,
                    name=new_name,
                    description=new_description,
                    private=new_private,
                )

                st.session_state.sf_gh_created_repo = created

                st.success(
                    f"Repository created: "
                    f"{created.get('full_name', new_name)}"
                )

                repos = list_repositories(token)
                st.session_state.sf_gh_repos = repos

            except Exception as exc:
                st.error(f"Repository creation failed: {exc}")
                return

        created = st.session_state.get("sf_gh_created_repo")

        if not created:
            return

        selected = created.get("full_name", "")

    if not selected:
        return

    # -------------------------------------------------------------------------
    # Functionality
    # -------------------------------------------------------------------------

    st.divider()
    st.subheader("3. Generated functionality")

    functionality = st.text_input(
        "Functionality name",
        placeholder="Pomodoro timer",
        help=(
            "Used to generate the professional feature branch name."
        ),
    )

    if not functionality.strip():
        st.warning("Enter the functionality name.")
        return

    branch = make_feature_branch_name(functionality)

    st.code(
        f"feature branch\n{branch}",
        language="text",
    )

    if branch in {
        "main",
        "master",
        "qa",
        "develop",
        "dev",
    }:
        st.error("Unsafe protected branch detected.")
        return

    # -------------------------------------------------------------------------
    # Local generated files
    # -------------------------------------------------------------------------

    st.divider()
    st.subheader("4. Generated files")

    try:
        local_changes = changed_files(project_root)
    except Exception as exc:
        st.error(f"Could not inspect generated files: {exc}")
        return

    if not local_changes:
        st.warning(
            "No uncommitted files are currently detected in "
            "the SOUL FORGE project."
        )

        st.caption(
            "Generate or modify the functionality first, then return here."
        )

        return

    selected_files = st.multiselect(
        "Files to deliver",
        local_changes,
        default=local_changes,
        help=(
            "Only selected files will be staged. "
            "Other working-tree changes remain untouched."
        ),
    )

    if not selected_files:
        st.warning("Select at least one generated file.")
        return

    # -------------------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------------------

    st.divider()
    st.subheader("5. Validation")

    if st.button(
        "🧪 Validate Selected Code",
        use_container_width=True,
    ):
        try:
            validation = validate_selected_files(
                project_root,
                selected_files,
            )

            st.session_state.sf_gh_validation = validation

        except Exception as exc:
            st.error(f"Validation failed: {exc}")
            return

    validation = st.session_state.get(
        "sf_gh_validation"
    )

    if validation:

        if validation.get("passed"):
            st.success(
                "All selected files passed validation."
            )
        else:
            st.error(
                "Validation failed. Fix the code before delivery."
            )

        for result in validation.get("files", []):
            if result.get("passed"):
                st.write(
                    f"✅ `{result.get('file')}` — "
                    f"{result.get('message')}"
                )
            else:
                st.write(
                    f"❌ `{result.get('file')}` — "
                    f"{result.get('message')}"
                )

    # -------------------------------------------------------------------------
    # Delivery
    # -------------------------------------------------------------------------

    st.divider()
    st.subheader("6. Feature branch delivery")

    commit_message = st.text_input(
        "Commit message",
        value=(
            f"feat(soul-forge): "
            f"add {functionality.strip().lower()}"
        ),
    )

    pr_title = st.text_input(
        "Pull Request title",
        value=f"feat(soul-forge): {functionality.strip()}",
    )

    pr_body = st.text_area(
        "Pull Request description",
        value=(
            "## SOUL FORGE Generated Change\n\n"
            f"### Functionality\n"
            f"{functionality.strip()}\n\n"
            "### Generated Files\n"
            + "\n".join(
                f"- `{file}`"
                for file in selected_files
            )
            + "\n\n"
            "### Validation\n"
            "- SOUL FORGE validation performed before delivery\n"
            "- Human QA review required\n\n"
            "### Merge Policy\n"
            "- Target branch: `qa`\n"
            "- `main` merge: manual only\n"
        ),
        height=220,
    )

    st.warning(
        "Delivery creates/uses a `feature/soul-forge-*` branch, "
        "pushes that branch, and opens a PR targeting `qa`."
    )

    if st.button(
        "🚀 Deliver to GitHub + Create PR → QA",
        type="primary",
        use_container_width=True,
    ):

        try:

            # -----------------------------------------------------------------
            # HARD SAFETY CHECK
            # -----------------------------------------------------------------

            if branch in {
                "main",
                "master",
                "qa",
            }:
                raise GitHubDeliveryError(
                    "BLOCKED: protected branch."
                )

            if not branch.startswith(
                "feature/soul-forge-"
            ):
                raise GitHubDeliveryError(
                    "BLOCKED: invalid SOUL FORGE feature branch."
                )

            if not validation or not validation.get("passed"):
                raise GitHubDeliveryError(
                    "Validation must pass before delivery."
                )

            # -----------------------------------------------------------------
            # Parse repository
            # -----------------------------------------------------------------

            remote = remote_url(project_root)

            owner, repo_name = parse_owner_repo(remote)

            # If selected repository differs from local origin, require
            # the selected repository to be used explicitly.
            selected_owner, selected_repo = selected.split(
                "/",
                1,
            )

            if (
                owner != selected_owner
                or repo_name != selected_repo
            ):
                raise GitHubDeliveryError(
                    "Selected GitHub repository does not match "
                    "the current local repository origin.\n\n"
                    f"Local origin: {owner}/{repo_name}\n"
                    f"Selected: {selected_owner}/{selected_repo}\n\n"
                    "Clone/configure the selected repository first "
                    "or use the current repository."
                )

            # -----------------------------------------------------------------
            # Create feature branch
            # -----------------------------------------------------------------

            st.write(
                f"🌿 Creating branch `{branch}`..."
            )

            create_feature_branch(
                project_root,
                branch,
            )

            # -----------------------------------------------------------------
            # Stage ONLY selected files
            # -----------------------------------------------------------------

            st.write(
                "📦 Staging selected generated files..."
            )

            stage_files(
                project_root,
                selected_files,
            )

            staged = staged_files(
                project_root
            )

            if not staged:
                raise GitHubDeliveryError(
                    "No files were staged."
                )

            st.write(
                f"📦 Staged {len(staged)} file(s)."
            )

            # -----------------------------------------------------------------
            # Commit
            # -----------------------------------------------------------------

            st.write(
                "📝 Creating commit..."
            )

            commit_sha = commit(
                project_root,
                commit_message,
            )

            st.write(
                f"📝 Commit: `{commit_sha[:12]}`"
            )

            # -----------------------------------------------------------------
            # Push feature branch
            # -----------------------------------------------------------------

            st.write(
                f"⬆️ Pushing `{branch}`..."
            )

            push_feature_branch(
                project_root,
                branch,
            )

            # -----------------------------------------------------------------
            # Create PR
            # -----------------------------------------------------------------

            st.write(
                "🔀 Creating Pull Request → qa..."
            )

            pr = create_pull_request(
                token=token,
                owner=selected_owner,
                repo=selected_repo,
                head=branch,
                base="qa",
                title=pr_title,
                body=pr_body,
            )

            pr_url = pr.get(
                "html_url",
                "",
            )

            manifest = delivery_manifest(
                functionality=functionality,
                branch=branch,
                files=staged,
                commit_message=commit_message,
                validation=validation,
                pr_url=pr_url,
            )

            st.session_state.sf_gh_pr = pr
            st.session_state.sf_gh_delivery_manifest = manifest

            # -----------------------------------------------------------------
            # SUCCESS
            # -----------------------------------------------------------------

            st.success(
                "SOUL FORGE delivery completed successfully."
            )

            st.write(
                f"🌿 Feature branch: `{branch}`"
            )

            st.write(
                "🎯 Pull Request target: `qa`"
            )

            if pr_url:
                st.link_button(
                    "🔀 Open Pull Request",
                    pr_url,
                    use_container_width=True,
                )

            st.info(
                "NEXT STEP: Review the Pull Request in GitHub. "
                "SOUL FORGE does not merge it into qa or main."
            )

        except Exception as exc:
            st.error(
                f"GitHub delivery failed: {exc}"
            )

    # -------------------------------------------------------------------------
    # Existing PR information
    # -------------------------------------------------------------------------

    existing_pr = st.session_state.get(
        "sf_gh_pr"
    )

    if existing_pr:
        st.divider()

        st.subheader("Delivery result")

        st.write(
            f"Branch: "
            f"`{existing_pr.get('head', {}).get('ref', branch)}`"
        )

        st.write(
            f"Target: "
            f"`{existing_pr.get('base', {}).get('ref', 'qa')}`"
        )

        if existing_pr.get("html_url"):
            st.link_button(
                "🔀 Open Pull Request",
                existing_pr["html_url"],
            )

        st.success(
            "Main branch remains untouched. "
            "Manual merge is required."
        )
