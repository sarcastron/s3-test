Yes, you can. In Google Cloud Platform (GCP), the best way to achieve this is by granting a **Bucket-Level IAM Role** to the service account.

By default, many people mistakenly grant permissions at the **Project Level**, which gives the service account access to *every* bucket in the project. To restrict it to a **specific** bucket, you apply the permission directly to that bucket’s individual policy.

### The Recommended Roles

To cover "read, view, list, and write," you generally need a combination of permissions. The simplest approach is to use the following predefined roles:

* **`roles/storage.objectAdmin`**: Grants full control over **objects** (read, write, list, delete).
* **`roles/storage.objectViewer`** + **`roles/storage.objectCreator`**: If you want to avoid giving "Delete" permissions, use this combination instead.

---

### How to set it up

#### Prerequisite

You will want to have a service account already created. If you don't already have one you want to use you can create one without any permissions (assigned roles). We will add the roles later for an individual bucket.

#### Method 1: Using the GCP Console (UI)

1. Go to the **Cloud Storage > Buckets** page.
2. Click on the **Name** of the specific bucket you want to grant access to.
3. Select the **Permissions** tab.
4. Click **Grant Access**.
5. In the **New principals** field, enter the email address of your service account.
6. In the **Select a role** dropdown, choose **Cloud Storage > Storage Object Admin** (or your preferred specific roles).
7. Click **Save**.

#### Method 2: Using `gcloud` CLI

Run the following command to bind the service account to the bucket:

```bash
gcloud storage buckets add-iam-policy-binding gs://YOUR_BUCKET_NAME \
    --member="serviceAccount:your-service-account@your-project.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

```

---

### Key Technical Details

* **Uniform Bucket-Level Access:** For the most consistent experience, ensure the bucket has **Uniform** access control enabled. This ensures that IAM policies (like the one you just set) apply to all objects in the bucket equally, ignoring legacy ACLs.
* **Project-level vs. Bucket-level:** Ensure the service account does **not** have storage roles at the Project level (IAM & Admin > IAM), otherwise, those permissions will "inherit" down to all buckets, overriding your bucket-specific restriction.
* **The "List" Permission:** Note that `storage.objects.list` allows the service account to see files inside the bucket. If the service account also needs to see the bucket *name* in the main GCS list in the Console, it would technically need `storage.buckets.list` at the project level, but for API/CLI usage (like `gsutil cp`), bucket-level access is sufficient.
