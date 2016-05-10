# Welcome to the Okta SCIM Beta

Thank you for your interest in the Okta SCIM beta.

If you haven't heard of SCIM before, here is a good summary from the
[Wikipedia article on SCIM](https://en.wikipedia.org/wiki/System_for_Cross-domain_Identity_Management):

> System for Cross-domain Identity Management (SCIM) is an open
> standard for automating the exchange of user identity information
> between identity domains, or IT systems.

If you are a developer for a cloud application, Okta allows you
to receive user provisioning and profile update message from Okta
using the open SCIM standard.

# Getting into the Okta SCIM Beta

Before building your SCIM Server, please [apply for admission to the
SCIM Beta](https://docs.google.com/forms/d/1RKvwFaY8hoMvWn2HEnIsXYY2uaDDZZtF8-p6h2a6e4E/viewform). Okta reviews new applicants on a weekly basis. We will
reply within 7 days and give you an estimated timeline.

Once admitted, we will collect information about your SCIM Server to
get a generic SCIM template application ready for testing. You will
need to be ready to provide:

1.  The oktapreview.com Okta org that you will use to develop your
    SCIM integration. (If you don't already have an Okta org, create
    an [Okta Developer account](https://www.okta.com/developer/signup/))
2.  The Base URL to which Okta will send SCIM requests to your
    service.
3.  The Authentication method that Okta will use to authenticate with
    your service.
4.  Details on the Base URL and Authentication method are covered
    below.

Once the generic SCIM template app is in your Okta org, you can
start testing on your SCIM integration directly with Okta.

# Understanding of User Provisioning in Okta

Okta is a universal directory with the main focus in storing
identity related information.  Users can be created in Okta directly
as local users or imported from external systems like Active
Directory or a [Human Resource Management Software](https://en.wikipedia.org/wiki/Category:Human_resource_management_software) system.

An Okta user schema contains many different user attributes,
but always contains a user name, first name, last name, and
email address. This schema can be extended.

Okta user attributes can be mapped from a source into Okta and can
be mapped from Okta to a target.

Below are the main operations in Okta's SCIM user provisioning lifecycle:

1.  Create a user account.
2.  Read a list of accounts, with support for searching for a preexisting account.
3.  Update an account (user profile changes, entitlement changes, etc).
4.  Deactivate an account.

In Okta, an application instance is a connector that provides Single Sign-On
and provisioning functionality with the target application.

# Required SCIM Capabilities

Okta supports provisioning to both SCIM 1.1 and SCIM 2.0 APIs.

If you haven't implemented SCIM, Okta recommends that you implement
SCIM 2.0.

Okta implements SCIM 2.0 as described in RFCs [7642](https://tools.ietf.org/html/rfc7642), [7643](https://tools.ietf.org/html/rfc7643), [7644](https://tools.ietf.org/html/rfc7644).

If you are writing a SCIM implementation for the first time, an
important part of the planning process is determining which of
Okta's provisioning features your SCIM API can or should support and
which features you do not need to support.

Specifically, you do not need to implement the SCIM 2.0
specification fully to work with Okta. At a minimum, Okta requires that
your SCIM 2.0 API implement the features described below:

## Base URL

The API endpoint for your SCIM API **MUST** be secured via [TLS](https://tools.ietf.org/html/rfc5246)
(`https://`), Okta *does not* connect to unsecured API endpoints.

You can choose any Base URL for your API endpoint. If you
are implementing a brand new SCIM API, we suggest using `/scim/v2`
as your Base URL; for example: `https://example.com/scim/v2` -
however, you must support the URL structure described in the
["SCIM Endpoints and HTTP Methods" section of RFC7644](https://tools.ietf.org/html/rfc7644#section-3.2).

## Authentication

Your SCIM API **MUST** be secured against anonymous access. At the
moment, Okta supports authentication against SCIM APIs with one of
the following methods:

1.  [OAuth 2.0](http://oauth.net/2/)
2.  [Basic Authentication](https://en.wikipedia.org/wiki/Basic_access_authentication)
3.  Custom HTTP Header

## Basic User Schema

Your service must be capable of storing the following four user
attributes:

1.  User ID (`userName`)
2.  First Name (`name.givenName`)
3.  Last Name (`name.familyName`)
4.  Email (`emails`)

Note that Okta supports more than the four user attributes listed
above. However, these four attributes are the base attributes that
you must support.  The full user schema for SCIM 2.0 is described
in [section 4 of RFC 7643](https://tools.ietf.org/html/rfc7643#section-4).

> **Best Practice:** Keep your User ID distinct from the User Email
> Address. Many systems use an email address as a user identifier,
> but this is not recommended, as email addresses often change. Using
> a unique User ID to identify user resources prevents future
> complications.

If your service supports user attributes beyond those four base
attributes, add support for those additional
attributes to your SCIM API. In some cases, you might need to
configure Okta to map non-standard user attributes into the user
profile for your application.

Included in this git repository is a sample application written in
Python/Flask, this sample application implements SCIM 2.0. Below is
how this sample application defines these attributes:

    userName = db.Column(db.String(250),
                         unique=True,
                         nullable=False,
                         index=True)
    familyName = db.Column(db.String(250))
    middleName = db.Column(db.String(250))
    givenName = db.Column(db.String(250))

In addition to the basic user schema user attributes described
above, your SCIM API must also have a unique identifier for each
user resource and should also support marking resources as "active"
or "inactive."

In the SCIM specification, the `id` attribute is used to uniquely
identify resources. [Section 3.1](//tools.ietf.org/html/rfc7643#section-3.1) of [RFC 7643](https://tools.ietf.org/html/rfc7643) provides more details
on the `id` attribute:

> A unique identifier for a SCIM resource as defined by the service
> provider.  Each representation of the resource MUST include a
> non-empty "id" value.  This identifier MUST be unique across the
> SCIM service provider's entire set of resources.  It MUST be a
> stable, non-reassignable identifier that does not change when the
> same resource is returned in subsequent requests.  The value of
> the "id" attribute is always issued by the service provider and
> MUST NOT be specified by the client.  The string "bulkId" is a
> reserved keyword and MUST NOT be used within any unique identifier
> value.  The attribute characteristics are "caseExact" as "true", a
> mutability of "readOnly", and a "returned" characteristic of
> "always".

Our sample application defines `id` as a UUID, since
[RFC 7643](https://tools.ietf.org/html/rfc7643) requires that "this identifier MUST be unique across the
SCIM service provider's entire set of resources."

    id = db.Column(db.String(36), primary_key=True)

**Note:** Your SCIM API can use anything as an `id`, provided that the `id`
uniquely identifies reach resource, as described in [section 3.1](https://tools.ietf.org/html/rfc7643#section-3.1) of
[RFC 7643](https://tools.ietf.org/html/rfc7643).

Finally, your SCIM API must also support marking a resource as
"active" or "inactive."

In our sample application, each user resource has a Boolean
"active" attribute which is used to mark a user resource as
"active" or "inactive":

    active = db.Column(db.Boolean, default=False)

## Functionality

Below are a list of the SCIM API endpoints that your SCIM API must
support to work with Okta.

## Create Account: POST /Users

Your SCIM 2.0 API should allow the creation of a new user
account.  The four basic attributes listed above must be supported, along
with any additional attributes that your application supports.  If your
application supports entitlements, your SCIM 2.0 API should allow
configuration of those as well.

An HTTP POST to the `/Users` endpoint must return an immutable or 
system ID of the user (`id`) must be returned to Okta.

Okta will call this SCIM API endpoint under the following circumstances:

-   **Direct assignment**
    
    When a user is assigned to an Okta application using the "Assign
    to People" button in the "People" tab.
-   **Group-based assignment**
    
    When a user is added to a group that is assigned to an Okta
    application. For example, an Okta administrator can assign a
    group of users to an Okta application using the "Assign to
    Groups" button in the "Groups" tab. When a group is assigned to an
    Okta application, Okta sends updates to the assigned
    application when a user is added or removed from that group.

Below is an example demonstrating how the sample application handles account
creation:

    @app.route("/scim/v2/Users", methods=['POST'])
    def users_post():
        user_resource = request.get_json(force=True)
        user = User(user_resource)
        user.id = str(uuid.uuid4())
        db.session.add(user)
        db.session.commit()
        rv = user.to_scim_resource()
        send_to_browser(rv)
        resp = flask.jsonify(rv)
        resp.headers['Location'] = url_for('user_get',
                                           user_id=user.userName,
                                           _external=True)
        return resp, 201

Note: `force=True` is set because Okta sends
`application/scim+json` as the `Content-Type` and the `.get_json()`
method expects `application/json`.

For more information on user creation via the `/Users` SCIM
endpoint, see [section 3.3](https://tools.ietf.org/html/rfc7644#section-3.3) of the [SCIM 2.0 Protocol Specification](https://tools.ietf.org/html/rfc7644).

## Read list of accounts with search: GET /Users

Your SCIM 2.0 API must support the ability for Okta to retrieve
users (and entitlements like groups if available) from your
service.  This allows Okta to fetch all user resources in an
efficient manner for reconciliation and initial bootstrap (to
get all users from your app into the system).

Below is how the sample application handles listing user resources,
with support for filtering and pagination:

    @app.route("/scim/v2/Users", methods=['GET'])
    def users_get():
        query = User.query
        request_filter = request.args.get('filter')
        match = None
        if request_filter:
            match = re.match('(\w+) eq "([^"]*)"', request_filter)
        if match:
            (search_key_name, search_value) = match.groups()
            search_key = getattr(User, search_key_name)
            query = query.filter(search_key == search_value)
        count = int(request.args.get('count', 100))
        start_index = int(request.args.get('startIndex', 1))
        if start_index < 1:
            start_index = 1
        start_index -= 1
        query = query.offset(start_index).limit(count)
        total_results = query.count()
        found = query.all()
        rv = ListResponse(found,
                          start_index=start_index,
                          count=count,
                          total_results=total_results)
        return flask.jsonify(rv.to_scim_resource())

> If you want to see the SQL query that SQLAlchemy is using for
> the query, add this code after the `query` statement that you want
> to see: `print(str(query.statement))`

For more details on the `/Users` SCIM endpoint, see [section 3.4.2](https://tools.ietf.org/html/rfc7644#section-3.4.2)
of the [SCIM 2.0 Protocol Specification](https://tools.ietf.org/html/rfc7644).

## Read Account Details: GET /Users/{id}

Your SCIM 2.0 API must support fetching of users by user id.

Below is how the sample application handles returning a user resource
by user id:

    @app.route("/scim/v2/Users/<user_id>", methods=['GET'])
    def user_get(user_id):
        user = User.query.filter_by(id=user_id).one()
        return render_json(user)

For more details on the `/Users/{id}` SCIM endpoint, see [section 3.4.1](https://tools.ietf.org/html/rfc7644#section-3.4.1)
of the [SCIM 2.0 Protocol Specification](https://tools.ietf.org/html/rfc7644).

## Update Account Details: PUT /Users/{id}

When a profile attribute of a user assigned to your SCIM enabled
application is changed, Okta will do the following:

-   Make a GET request against `/Users/{id}` on your SCIM API for the
    user to update.
-   Take the resource returned from your SCIM API and update only the
    attributes that need to be updated.
-   Make a PUT request against `/Users/{id}` in your SCIM API with
    the updated resource as the payload.

Examples of things that can cause changes to an Okta user profile
are:

-   A change in profile a master like Active Directory or a Human Resource
    Management Software system.
-   A direct change of a profile attribute in Okta for a local user.

Below is how the sample application handles account profile updates:

    @app.route("/scim/v2/Users/<user_id>", methods=['PUT'])
    def users_put(user_id):
        user_resource = request.get_json(force=True)
        user = User.query.filter_by(id=user_id).one()
        user.update(user_resource)
        db.session.add(user)
        db.session.commit()
        return render_json(user)

For more details on updates to the `/Users/{id}` SCIM endpoint, see [section 3.5.1](https://tools.ietf.org/html/rfc7644#section-3.5.1)
of the [SCIM 2.0 Protocol Specification](https://tools.ietf.org/html/rfc7644).

## Deactivate Account: PATCH /Users/{id}

Deprovisioning is perhaps the most important reason customers why
customers ask that your application supports provisioning
with Okta. Your SCIM API should support account deactivation via a
PATCH to `/Users/{id}` where the payload of the PATCH request sets
the `active` property of the user to `false`.

Your SCIM API should allow account updates at the attribute level.
If entitlements are supported, your SCIM API should also be able
to update entitlements based on SCIM profile updates.

Okta will send a PATCH request to your application to deactivate a
user when an Okta user is "unassigned" from your
application. Examples of when this happen are as follows:

-   A user is manually unassigned from your application.
-   A user is removed from a group which is assigned to your application.
-   When a user is deactivated in Okta, either manually or via 
    by an external profile master like Active Directory or a Human
    Resource Management Software system.

Below is how the sample application handles account deactivation:

    @app.route("/scim/v2/Users/<user_id>", methods=['PATCH'])
    def users_patch(user_id):
        patch_resource = request.get_json(force=True)
        for attribute in ['schemas', 'Operations']:
            if attribute not in patch_resource:
                message = "Payload must contain '{}' attribute.".format(attribute)
                return message, 400
        schema_patchop = 'urn:ietf:params:scim:api:messages:2.0:PatchOp'
        if schema_patchop not in patch_resource['schemas']:
            return "The 'schemas' type in this request is not supported.", 501
        user = User.query.filter_by(id=user_id).one()
        for operation in patch_resource['Operations']:
            if 'op' not in operation and operation['op'] != 'replace':
                continue
            value = operation['value']
            for key in value.keys():
                setattr(user, key, value[key])
        db.session.add(user)
        db.session.commit()
        return render_json(user)

For more details on user attribute updates to `/Users/{id}` SCIM endpoint, see [section 3.5.2](https://tools.ietf.org/html/rfc7644#section-3.5.2)
of the [SCIM 2.0 Protocol Specification](https://tools.ietf.org/html/rfc7644).

## Filtering on `id`, `userName`, and `emails`

Being able to filter results by the `id`, `userName`, or `emails`
attributes is a critical part of working with Okta. 

Your SCIM API must be able to filter users by `userName` and should
also support filtering by `id` and `emails`. Filtering support
is required because most provisioning actions require the ability
for Okta to determine if a user resource exists on your system.

Consider the scenario where an Okta customer with thousands of
users has a provisioning integration with your system, which also
has thousands of users. When an Okta customer adds a new user to
their Okta organization, Okta needs a way to determine quickly if a
resource for the newly created user was previously created on your
system.

Examples of filters that Okta might send to your SCIM API are as
follows:

> userName eq "jane@example.com"

> emails eq "jane@example.com"

At the moment, Okta only supports the `eq` filter operator. However, the
[filtering capabilities](https://tools.ietf.org/html/rfc7644#section-3.4.2.2) described in the SCIM 2.0 Protocol Specification are
much more complicated.

Here is an example of how to implement SCIM filtering in Python:

    request_filter = request.args.get('filter')
    match = None
    if request_filter:
        match = re.match('(\w+) eq "([^"]*)"', request_filter)
    if match:
        (search_key_name, search_value) = match.groups()
        search_key = getattr(User, search_key_name)
        query = query.filter(search_key == search_value)

Note: The sample code above only supports the `eq` operator. We
recommend that you add support for all of the filter operators
described in [table 3](https://tools.ietf.org/html/rfc7644#page-18) of the SCIM 2.0 Protocol Specification.

For more details on filtering in SCIM 2.0, see [section 3.4.2.2](https://tools.ietf.org/html/rfc7644#section-3.4.2.2)
of the [SCIM 2.0 Protocol Specification](https://tools.ietf.org/html/rfc7644).

## Filtering on `externalId`

In addition to supporting filtering on `id`, `userName`, and
`emails`, your application should also support filtering on
`externalId`.

Okta will use the `externalId` to determine if your application
already has an account. `externalId` is used as a stable identifier
for users, because the `userName` and email addresses for a user
can change.

Here is an example of an `externalId` filter that might be sent to
your application:

> externalId eq "00u1abcdefGHIJKLMNOP"

Note: The sample application included in this project does not yet
demonstrate how to implement storing and filtering by
`externalId`. However, Okta strongly recommends that your SCIM
implementation supports storing and filtering by `externalId`. For
details on supporting `externalId`, see
[section 3.1](https://tools.ietf.org/html/rfc7643#section-3.1) of [RFC 7643](https://tools.ietf.org/html/rfc7643). Quoted below:

> [externalId is] A String that is an identifier for the resource
> as defined by the provisioning client.  The "externalId" may
> simplify identification of a resource between the provisioning
> client and the service provider by allowing the client to use a
> filter to locate the resource with an identifier from the
> provisioning domain, obviating the need to store a local mapping
> between the provisioning domain's identifier of the resource and
> the identifier used by the service provider.  Each resource MAY
> include a non-empty "externalId" value.  The value of the
> "externalId" attribute is always issued by the provisioning
> client and MUST NOT be specified by the service provider.  The
> service provider MUST always interpret the externalId as scoped
> to the provisioning domain.  While the server does not enforce
> uniqueness, it is assumed that the value's uniqueness is
> controlled by the client setting the value.

When adding support for `externalId` filtering to your application,
we suggest that you use OAuth2.0 for authentication and use the
OAuth2.0 `client_id` to scope the `externalId` to the provisioning
domain.

## Resource Paging

When returning large lists of resources, your SCIM implementation
must support pagination using a *limit* (`count`) and *offset*
(`startIndex`) to return smaller groups of resources in a request.

Below is an example of a `curl` command that makes a request to the
`/Users/` SCIM endpoint with `count` and `startIndex` set:

    $ curl 'https://scim-server.example.com/scim/v2/Users?count=1&startIndex=1'
    {
      "Resources": [
        {
          "active": false, 
          "id": 1, 
          "meta": {
            "location": "http://scim-server.example.com/scim/v2/Users/1", 
            "resourceType": "User"
          }, 
          "name": {
            "familyName": "Doe", 
            "givenName": "Jane", 
            "middleName": null
          }, 
          "schemas": [
            "urn:ietf:params:scim:schemas:core:2.0:User"
          ], 
          "userName": "jane.doe@example.com"
        }
      ], 
      "itemsPerPage": 1, 
      "schemas": [
        "urn:ietf:params:scim:api:messages:2.0:ListResponse"
      ], 
      "startIndex": 0, 
      "totalResults": 1
    }

> Note: When returning a paged resource, your API should return a
> capitalized `Resources` JSON key ("Resources"), however Okta will also
> support a lowercase string ("resources"). Okta will also accept
> lowercased JSON strings for the keys of child nodes inside
> `Resources` object ("startindex", "itemsperpage", "totalresults", etc)

One way to handle paged resources is to have your database do the
paging for you. Here is how the sample application handles
pagination with SQLAlchemy:

    count = int(request.args.get('count', 100))
    start_index = int(request.args.get('startIndex', 1))
    if start_index < 1:
        start_index = 1
    start_index -= 1
    query = query.offset(start_index).limit(count)

Note: This code subtracts "1" from the
`startIndex`, because `startIndex` is [1-indexed](https://tools.ietf.org/html/rfc7644#section-3.4.2) and
the OFFSET statement is [0-indexed](http://www.postgresql.org/docs/8.0/static/queries-limit.html).

For more details pagination on a SCIM 2.0 endpoint, see [section 3.4.2.4](https://tools.ietf.org/html/rfc7644#section-3.4.2.4)
of the [SCIM 2.0 Protocol Specification](https://tools.ietf.org/html/rfc7644).

## Rate Limiting

Some customer actions, such as adding hundreds of users at once,
causes large bursts of HTTP requests to your SCIM API. For
scenarios like this, we suggest that your SCIM API return rate
limiting information to Okta via the [HTTP 429 Too Many Requests](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#429)
status code. This helps Okta throttle the rate at which SCIM
requests are made to your API.

For more details on rate limiting requests using the HTTP 429
status code, see [section 4](https://tools.ietf.org/html/rfc6585#section-4) of [RFC 6585](https://tools.ietf.org/html/rfc6585).

## SCIM Features Not Implemented by Okta

The following features are currently not supported by Okta:

### DELETE /Users/{id}

Deleting users via DELETE is covered in
[section 3.6](https://tools.ietf.org/html/rfc7644#section-3.6) of the [SCIM 2.0 Protocol Specification](https://tools.ietf.org/html/rfc7644).

Okta users are never **deleted**; they are **deactivated**
instead. Because of this, Okta never makes an HTTP DELETE
request to a user resource on your SCIM API. Instead, Okta makes
an HTTP PATCH request to set the `active` setting to `false`.

### Querying with POST

The ability to query users with a POST request is described in
[section 3.4.3](https://tools.ietf.org/html/rfc7644#section-3.4.3) of the [SCIM 2.0 Protocol Specification](https://tools.ietf.org/html/rfc7644).

Querying using POST is sometimes useful if your query contains 
[personally identifiable information](https://en.wikipedia.org/wiki/Personally_identifiable_information) that would be exposed in
system logs if used query parameters with a GET request.

Okta currently does not support this feature.

### Bulk Operations

The ability to send a large collection of resource operations in a
single request is covered in
[section 3.7](https://tools.ietf.org/html/rfc7644#section-3.7) of the [SCIM 2.0 Protocol Specification](https://tools.ietf.org/html/rfc7644).

Okta currently does not support this feature and makes
one request per resource operation.

### "/Me" Authenticated Subject Alias

The `/Me` URI alias for the current authenticated subject is
covered in
[section 3.11](https://tools.ietf.org/html/rfc7644#section-3.11) of the [SCIM 2.0 Protocol Specification](https://tools.ietf.org/html/rfc7644).

Okta does not currently make SCIM requests with the `/Me` URI alias.

### /Groups API endpoint

Okta currently does not support using the `/Groups` endpoint of a SCIM
API. When support is added for the `/Groups` endpoint, Okta plans
on using the following HTTP requests against the `/Groups` endpoint:

-   Read list of Groups: GET /Groups

-   Create Group: POST /Groups

-   Read Group detail: GET /Groups/{id}

-   Delete Group: DELETE /Groups/{id}

### /Schemas API endpoint

Okta does not currently make queries against the `/Schemas`
endpoint, but this functionality is being planned.

Here is the specification for the `/Schemas` endpoint, from
[section 4](https://tools.ietf.org/html/rfc7644#section-4) of [RFC 7644](https://tools.ietf.org/html/rfc7644):

> An HTTP GET to this endpoint is used to retrieve information about
> resource schemas supported by a SCIM service provider.  An HTTP
> GET to the endpoint "/Schemas" SHALL return all supported schemas
> in ListResponse format (see Figure 3).  Individual schema
> definitions can be returned by appending the schema URI to the
> /Schemas endpoint.  For example:
> 
> /Schemas/urn:ietf:params:scim:schemas:core:2.0:User
> 
> The contents of each schema returned are described in Section 7 of
> RFC7643.  An example representation of SCIM schemas may be found
> in Section 8.7 of RFC7643.

### /ServiceProviderConfig API endpoint

Okta does not currently make queries against the `/ServiceProviderConfig`
endpoint, but this functionality is being planned.

Here is the specification for the `/ServiceProviderConfig` endpoint, from
[section 4](https://tools.ietf.org/html/rfc7644#section-4) of [RFC 7644](https://tools.ietf.org/html/rfc7644):

> An HTTP GET to this endpoint will return a JSON structure that
> describes the SCIM specification features available on a service
> provider.  This endpoint SHALL return responses with a JSON object
> using a "schemas" attribute of
> "urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig".
> The attributes returned in the JSON object are defined in
> Section 5 of RFC7643.  An example representation of SCIM service
> provider configuration may be found in Section 8.5 of RFC7643.

### Filtering on `meta.lastModified`

Okta does not currently make queries for resources using
`meta.lastModified` as part of a filter expression.

Okta plans to add functionality to fetch incremental updates
from SCIM APIs by querying for resources using a filter expression
that requests resources which were updated since the last update.

This will likely be done using the `gt` filter operator. For
example:

> filter=meta.lastModified gt "2011-05-13T04:42:34Z"

# Submitting to Okta

Once you have SCIM provisioning working in your Okta application,
the last thing to do before submitting your
application to Okta is the following:

1.  Check the Profile Attributes for your application.
2.  Check the Attribute Mappings for your application.

## Check the Profile Attributes for Your Application

Before submitting your application to Okta, you should check the
User Attributes to make sure that the attributes are set to what
you would want your users to see.

Check your Profile Attributes as follows:

-   From the "Admin" section in Okta, open the settings page for your
    application.
-   In the "Provisioning" tab, scroll to the bottom and click the
    "Edit Attributes" button in the "User Attributes" section.
-   A "Profile Editor" screen will open, check the following settings:
    -   The "Display name" for the application
    -   The "Description"
    -   In the "Attributes" section, remove all attributes that are not
        supported by your application.
        
        This is an important step! Your users will get confused if your
        application appears to support attributes that are not
        supported by your SCIM API.
        
        You can delete an attribute by selecting an attribute, then
        clicking the "Delete" button located in right hand attribute details pane.
    -   After you've removed all unsupported attributes from the
        "Attributes" section, check through the remaining
        attributes. In particular, check that the following properties
        for each attribute are what you expect them to be:
        -   Display name
        -   Variable name
        -   External name
        -   External namespace
        -   Data type
        -   Attribute required
            Only mark an attribute as required if one of the following is
            true:
            1.  The attribute **must** be set for your provisioning
                integration to work.
            2.  An Okta administrator must populate a value for
                this attribute.
        -   Scope
    -   If the settings for any of your supported user attributes are
        incorrect, contact Okta and request the correction for your
        attribute.
    
    Click the blue "Back to profiles" link when you are done checking
    the Profile Attributes for your application.

## Check the Attribute Mappings for Your Application

The last step for you to complete before submitting your
application to Okta is to check the User Profile Mappings for your
application. These mappings are what determine how profile
attributes are mapped to and from your application to an Okta
user's Universal Directory profile.

To check the User Profile Mappings for your application, do the
following:

-   From the "Admin" section in Okta, open the settings page for your
    application.
-   In the "Provisioning" tab, scroll to the bottom and click the
    "Edit Mappings" button in the "Attribute Mappings" section.
-   Check that each mapping is what you would expect it to be. Be
    sure to check both of the followign:
    1.  From your application to Okta.
    2.  From Okta to your application.

## Contact Okta

After you've finished verifying that your SCIM API works with Okta,
it is time to submit your application to Okta.

Work with your contact at Okta to start your submission.

If you have any questions about this document, or how to work with
SCIM, send an email to [developers@okta.com](developers@okta.com).

# Appendix: Details on the example SCIM server

Included in this git repository is an example SCIM server written in
Python. 

This example SCIM server demonstrates how to implement a basic SCIM
server that can create, read, update, and deactivate Okta users.

The "Required SCIM Capabilities" section has the sample code that
handles the HTTP requests to this sample application, below we
describe the rest of code used in the example.

## How to run

This example code was written for **Python 2.7** and does not
currently work with Python 3.

Here is how to run the example code on your machine:

First, start by doing a `git checkout` of this repository, then
`cd` to directory that `git` creates. Then, do the following:

1.  Create an isolated Python environment named "venv" using [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/):
    
        $ virtualenv venv
2.  Next, activate the newly created virtualenv:
    
        $ source venv/bin/activate
3.  Then, install the dependencies for the sample SCIM server using
    Python's ["pip" package manager](https://en.wikipedia.org/wiki/Pip_%28package_manager%29):
    
        $ pip install -r requirements.txt
4.  Finally, start the example SCIM server using this command:
    
        $ python scim-server.py

## Introduction

Below are instructions for writing a SCIM server in Python, using
Flask and SQLAlchemy.

A completed version of this example server is available in this git
repository in the file named `scim-server.py`.

## Imports

We start by importing the Python packages that the SCIM server will
use:

    import os
    import re
    import uuid
    
    from flask import Flask
    from flask import render_template
    from flask import request
    from flask import url_for
    from flask_socketio import SocketIO
    from flask_socketio import emit
    from flask_sqlalchemy import SQLAlchemy
    import flask

## Setup

`re` adds support for regular expression parsing, `flask` adds the Flask
web framework, `flask_socketio` and `flask_sqlalchemy` add a idiomatic support for
their respective technologies to Flask.

Next we initialize Flask, SQLAlchemy, and SocketIO:

    app = Flask(__name__)
    database_url = os.getenv('DATABASE_URL', 'sqlite:///test-users.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    db = SQLAlchemy(app)
    socketio = SocketIO(app)

## SQLAlchemy support for the "users" table:

Below is the class that SQLAlchemy uses to give us easy access to
the "users" table.

The `update` method is used to "merge" or "update" a new User object
into an existing User object. This is used to simplify the code for
the code that handles PUT calls to `/Users/{id}`.

The `to_scim_resource` method is used to turn a User object into
a [SCIM "User" resource schema](https://tools.ietf.org/html/rfc7643#section-4.1).

    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.String(36), primary_key=True)
        active = db.Column(db.Boolean, default=False)
        userName = db.Column(db.String(250),
                             unique=True,
                             nullable=False,
                             index=True)
        familyName = db.Column(db.String(250))
        middleName = db.Column(db.String(250))
        givenName = db.Column(db.String(250))
    
        def __init__(self, resource):
            self.update(resource)
    
        def update(self, resource):
            for attribute in ['userName', 'active']:
                if attribute in resource:
                    setattr(self, attribute, resource[attribute])
            for attribute in ['givenName', 'middleName', 'familyName']:
                if attribute in resource['name']:
                    setattr(self, attribute, resource['name'][attribute])
    
        def to_scim_resource(self):
            rv = {
                "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
                "id": self.id,
                "userName": self.userName,
                "name": {
                    "familyName": self.familyName,
                    "givenName": self.givenName,
                    "middleName": self.middleName,
                },
                "active": self.active,
                "meta": {
                    "resourceType": "User",
                    "location": url_for('user_get',
                                        user_id=self.id,
                                        _external=True),
                    # "created": "2010-01-23T04:56:22Z",
                    # "lastModified": "2011-05-13T04:42:34Z",
                }
            }
            return rv

## Support for SCIM Query resources

We also define a `ListResponse` class, which is used to return an
array of SCIM resources into a
[Query Resource](https://tools.ietf.org/html/rfc7644#section-3.4.2).

    class ListResponse():
        def __init__(self, list, start_index=1, count=None, total_results=0):
            self.list = list
            self.start_index = start_index
            self.count = count
            self.total_results = total_results
    
        def to_scim_resource(self):
            rv = {
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
                "totalResults": self.total_results,
                "startIndex": self.start_index,
                "Resources": []
            }
            resources = []
            for item in self.list:
                resources.append(item.to_scim_resource())
            if self.count:
                rv['itemsPerPage'] = self.count
            rv['Resources'] = resources
            return rv

## Support for SCIM error messages

Given a `message` and HTTP `status_code`, this will return a Flask
response with the appropriately formatted SCIM error message.

By default, this function will return an HTTP status of "[HTTP 500
Internal Server Error](https://tools.ietf.org/html/rfc2068#section-10.5.1)". However you should return a more specific
`status_code` when possible.

See [section 3.12](https://tools.ietf.org/html/rfc7644#section-3.12) of [RFC 7644](https://tools.ietf.org/html/rfc7644) for details.

    def scim_error(message, status_code=500):
        rv = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
            "detail": message,
            "status": str(status_code)
        }
        return flask.jsonify(rv), status_code

## Socket.IO support

This sample application makes use of Socket.IO to give you a "real
time" view of SCIM requests that Okta makes to this sample
application.

When you load the sample application (the "/" route), your browser
will be sent a web application that uses Socket.IO to display
updates without the need for you to reload the page:

    @app.route('/')
    def hello():
        return render_template('base.html')

This page is updated using the functions below:

-   `send_to_browser` is syntactic sugar that will `emit` Socket.IO
    messages to the browser with the proper `broadcast` and
    `namespace` settings.
-   `render_json` is more syntactic sugar which is used to render
    JSON replies to Okta's SCIM client and `emit` the SCIM resource
    to Socket.IO at the same time.
-   `test_connect` is the function called with a browser first starts
    up Socket.IO, it returns a list of currently active users to the
    browser via Socket.IO.
-   `test_disconnect` is a stub that shows how to handle Socket.IO
    "disconnect" messages.

The code described above is as follows:

    def send_to_browser(obj):
        socketio.emit('user',
                      {'data': obj},
                      broadcast=True,
                      namespace='/test')
    
    
    def render_json(obj):
        rv = obj.to_scim_resource()
        send_to_browser(rv)
        return flask.jsonify(rv)
    
    
    @socketio.on('connect', namespace='/test')
    def test_connect():
        for user in User.query.filter_by(active=True).all():
            emit('user', {'data': user.to_scim_resource()})
    
    
    @socketio.on('disconnect', namespace='/test')
    def test_disconnect():
        print('Client disconnected')

## Socket.IO application

Below is the JavaScript that powers the Socket.IO application
described above. For the full contents of the HTML that this
JavaScript is part of, see the `base.html` file in the `templates`
directory of this project.

    $(document).ready(function () {
        namespace = '/test'; // change to an empty string to use the global namespace
        var uri = 'https://' + document.domain  + namespace;
        console.log(uri);
        var socket = io.connect(uri);
    
        socket.on('user', function(msg) {
            console.log(msg);
            var user = msg.data;
            var user_element = '#' + user.id
            var userRow = '<tr id="' + user.id + '"><td>' + user.id + '</td><td>' + user.name.givenName + '</td><td>' + user.name.familyName + '</td><td>' + user.userName + '</td></tr>';
            if($(user_element).length && user.active) {
                $(user_element).replaceWith(userRow);
            } else if (user.active) {
                $('#users-table').append(userRow);
            }
    
            if($(user_element).length && user.active) {
                $(user_element).show();
            }
            if($(user_element).length && !user.active) {
                $(user_element).hide();
            }
        });
    });

## Support for running from the command line

This bit of code allows you to run the sample application by typing
`python scim-server.py` from your command line.

This code also includes a `try/catch` block that creates all tables
of the `User.query.one()` function throws an error (which should
only happen if the User table isn't defined.

    if __name__ == "__main__":
        try:
            User.query.one()
        except:
            db.create_all()
        app.debug = True
        socketio.run(app)
        
## Frequently Ask Questions (FAQ)
   
* What are the differences between SCIM 1.1 and 2.0?    
   
| Section | SCIM 1.1 | SCIM 2.0 | Notes |
| --- | --- | --- | --- |
| Namespaces | <ul><li>urn:scim:schemas:core:1.0</li><li>urn:scim:schemas:extension:enterprise:1.0</li><ul> | <ul><li>urn:ietf:params:scim:schemas:core:2.0:User</li><li>urn:ietf:params:scim:schemas:extension:enterprise:2.0:User</li><ul> | Namespaces are different therefore 2.0 is not backwards compatible with 1.1 |
| Service Provider Config Endpoint | /ServiceProviderConfig<b>s</b> | /ServiceProviderConfig | Notice 2.0 does NOT have an 's' at the end |
| Patch Protocol | [Section 3.3.2](http://www.simplecloud.info/specs/draft-scim-api-01.html#edit-resource-with-patch) | [Section 3.5.2: Uses JSON Patch](https://tools.ietf.org/html/rfc7644#section-3.5.2) | |
| Error Response Schema | [Section 3.9](http://www.simplecloud.info/specs/draft-scim-api-01.html#anchor6) | [Section 3.12](https://tools.ietf.org/html/rfc7644#section-3.12) | |
| Reference Type | N/A | Supports ref type pointing to the full url of another SCIM Resource | |
| Query by POST /search | N/A | [Section 3.4.3](https://tools.ietf.org/html/rfc7644#section-3.4.3) | |  
| Media Type | [Section 3.6](http://www.simplecloud.info/specs/draft-scim-api-01.html#io-format): Accept: application/json | [Section 8.1](https://tools.ietf.org/html/rfc7644#section-8.1): Accept: application/scim+json | |

* What if the SCIM 1.1 spec isn't clear on a specific use case or scenario?   

    Okta recommends looking at the SCIM 2.0 spec for more clarification.  The SCIM 2.0 spec provides more guidelines and examples for various scenario's.

*  Why do I need to implement the 'type' attribute for attributes such as emails/phoneNumbers/addresses?

    The SCIM User Profile allows for an array of emails.  The only way to differentiate between emails is to use the 'type' sub-attribute.  The SCIM spec recommends in [Section 2.4](https://tools.ietf.org/html/rfc7643#section-2.4)
> When returning multi-valued attributes, service providers SHOULD
> canonicalize the value returned (e.g., by returning a value for the
> sub-attribute "type", such as "home" or "work") when appropriate
> (e.g., for email addresses and URLs).
>
> Service providers MAY return element objects with the same "value"
> sub-attribute more than once with a different "type" sub-attribute
> (e.g., the same email address may be used for work and home) but
> SHOULD NOT return the same (type, value) combination more than once
> per attribute, as this complicates processing by the client.
>
> When defining schema for multi-valued attributes, it is considered a
> good practice to provide a type attribute that MAY be used for the
> purpose of canonicalization of values.  In the schema definition for
> an attribute, the service provider MAY define the recommended
> canonical values (see Section 7).

* I only have one email/phone number/address in my user profile.  Do I need to implement the array of emails/phone numbers/addresses?

    Yes, the server should return these fields in an array which is specified in the SCIM spec as a multi-valued attribute. [Section 2.4](https://tools.ietf.org/html/rfc7643#section-2.4)

## Dependencies

Here is a detailed list of the dependencies that this example SCIM
server depends on, and what each dependency does.

<table id="requirements-table" border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="left" />

<col  class="left" />

<col  class="right" />

<col  class="left" />

<col  class="left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="left">name</th>
<th scope="col" class="left">equality</th>
<th scope="col" class="right">version</th>
<th scope="col" class="left">description</th>
<th scope="col" class="left">url</th>
</tr>
</thead>

<tbody>
<tr>
<td class="left">Flask</td>
<td class="left">>=</td>
<td class="right">0.10.1</td>
<td class="left">A web framework built with a small core and easy-to-extend philosophy.</td>
<td class="left">`http://flask.pocoo.org`</td>
</tr>


<tr>
<td class="left">Flask-SQLAlchemy</td>
<td class="left">>=</td>
<td class="right">2.1</td>
<td class="left">Adds SQLAlchemy support to Flask.</td>
<td class="left">`https://github.com/mitsuhiko/flask-sqlalchemy`</td>
</tr>


<tr>
<td class="left">Flask-SocketIO</td>
<td class="left">>=</td>
<td class="right">2.1</td>
<td class="left">Socket.IO integration for Flask applications.</td>
<td class="left">`https://github.com/miguelgrinberg/Flask-SocketIO`</td>
</tr>


<tr>
<td class="left">gunicorn</td>
<td class="left">>=</td>
<td class="right">19.4.5</td>
<td class="left">A pre-fork worker model HTTP server for WSGI.</td>
<td class="left">`https://en.wikipedia.org/wiki/Gunicorn_%28HTTP_server%29`</td>
</tr>


<tr>
<td class="left">Jinja2</td>
<td class="left">>=</td>
<td class="right">2.8</td>
<td class="left">A modern and designer-friendly templating language.</td>
<td class="left">`http://jinja.pocoo.org/docs/dev`</td>
</tr>


<tr>
<td class="left">MarkupSafe</td>
<td class="left">>=</td>
<td class="right">0.23</td>
<td class="left">A library for Python that implements a unicode string.</td>
<td class="left">`http://www.pocoo.org/projects/markupsafe`</td>
</tr>


<tr>
<td class="left">SQLAlchemy</td>
<td class="left">>=</td>
<td class="right">1.0.12</td>
<td class="left">SQL toolkit and Object Relational Mapper.</td>
<td class="left">`https://pypi.python.org/pypi/SQLAlchemy`</td>
</tr>


<tr>
<td class="left">Werkzeug</td>
<td class="left">>=</td>
<td class="right">0.11.4</td>
<td class="left">A WSGI utility library for Python.</td>
<td class="left">`http://werkzeug.pocoo.org`</td>
</tr>


<tr>
<td class="left">itsdangerous</td>
<td class="left">>=</td>
<td class="right">0.24</td>
<td class="left">Used to send data to untrusted environments.</td>
<td class="left">`http://pythonhosted.org/itsdangerous`</td>
</tr>


<tr>
<td class="left">python-engineio</td>
<td class="left">>=</td>
<td class="right">0.8.8</td>
<td class="left">Implementation of the Engine.IO realtime server.</td>
<td class="left">`https://github.com/miguelgrinberg/python-engineio`</td>
</tr>


<tr>
<td class="left">python-socketio</td>
<td class="left">>=</td>
<td class="right">1.0</td>
<td class="left">Implementation of the Socket.IO realtime server.</td>
<td class="left">`https://github.com/miguelgrinberg/python-socketio`</td>
</tr>


<tr>
<td class="left">six</td>
<td class="left">>=</td>
<td class="right">1.10.0</td>
<td class="left">Python 2 and 3 compatibility library.</td>
<td class="left">`https://pypi.python.org/pypi/six`</td>
</tr>


<tr>
<td class="left">wsgiref</td>
<td class="left">>=</td>
<td class="right">0.1.2</td>
<td class="left">Provides validation support for WSGI.</td>
<td class="left">`https://pypi.python.org/pypi/wsgiref`</td>
</tr>


<tr>
<td class="left">psycopg2</td>
<td class="left">&#xa0;</td>
<td class="right">&#xa0;</td>
<td class="left">Popular PostgreSQL adapter.</td>
<td class="left">`http://initd.org/psycopg/`</td>
</tr>
</tbody>
</table>

(This table is used to generate the `requirements.txt` file for this project)

# License information

    Copyright © 2016, Okta, Inc.
    
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
    
        http://www.apache.org/licenses/LICENSE-2.0
    
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
