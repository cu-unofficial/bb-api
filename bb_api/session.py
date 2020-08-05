import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import time

BASE_URL = "https://cuchd.blackboard.com"
AUTHENTICATE_URL = BASE_URL + "/webapps/login/"
BASE_API_URL = BASE_URL + "/learn/api/v1"

ENDPOINTS = {
    "courses"       : BASE_API_URL + "/users/_82232_1/memberships",
    "course"        : BASE_API_URL + "/courses/",
    "launch_session": BASE_API_URL + "/courses/{course_id}/collabultra/sessions/{session_id}/launch"
}

def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset


class SessionBlackBoard:
    def __init__(self, uid, password):
        self._courses = None
        self._cookies = self._login(uid, password)

    def _login(self, uid, password):
        login_page = requests.get(BASE_URL)
        soup = BeautifulSoup(login_page.text, "html.parser")
        nonce = soup.find("input", {"name": "blackboard.platform.security.NonceUtil.nonce"})
        data = {
            'user_id': uid,
            'password': password,
            'login': 'Sign In',
            'action': 'login',
            'new_loc': '',
            'blackboard.platform.security.NonceUtil.nonce': nonce["value"]
        }
        login = requests.post(AUTHENTICATE_URL, cookies=login_page.cookies, data=data, allow_redirects=False)
        return login.cookies

    def course(self, course_id):
        return Course(course_id, self._cookies)

    @property
    def courses(self):
        if self._courses is None:
            self._courses = self._get_courses()
        return self._courses

    def _get_courses(self):
        params = (
            ('expand', 'course.effectiveAvailability,course.permissions,courseRole'),
            ('includeCount', 'true'),
            ('limit', '10000'),
        )
        response = requests.get(ENDPOINTS["courses"], params=params, cookies=self._cookies)
        items = response.json()
        courses = [Course(item["courseId"], self._cookies) for item in items["results"]]
        return courses


class Course:
    def __init__(self, course_id, cookies):
        self.course_id = course_id
        self._cookies = cookies
        self._course = None
        self._sessions = None

    def __repr__(self):
        return "Course<(course_id={})>".format(self.course_id)

    @property
    def course(self):
        if not self._course:
            self._course = self._get_course_information()
        return self._course

    def _get_course_information(self):
        params = (
            ('expand', 'instructorsMembership, instructorsMembership.courseRole, effectiveAvailability, isChild'),
        )
        course_url = ENDPOINTS["course"] + self.course_id
        response = requests.get(course_url, params=params, cookies=self._cookies)
        return response.json()

    @property
    def sessions(self):
        if not self._sessions:
            self._sessions = self._get_sessions()
        return self._sessions

    def _get_sessions(self):
        params = (
            ('expand', 'sessionInstances'),
        )
        sessions_url = ENDPOINTS["course"] + self.course_id + '/collabultra/sessions'
        response = requests.get(sessions_url, params=params, cookies=self._cookies)
        sessions = [ Session(session, self.course, self._cookies) for session in response.json()["results"] ]
        return sessions

    def next_session(self):
        mapping = {}
        for session in self.sessions:
            occurrence = session.next_occurrence()
            if occurrence is not None:
                mapping[session] = occurrence
        items = mapping.items()
        if len(items) > 0:
            return min(items, key=lambda x: x[1]["startTime"])[0]
        else:
            return None

    def next_occurrence(self):
        session = self.next_session()
        if session is None:
            return None
        else:
            return session.next_occurrence()


class Session:
    def __init__(self, session, course, cookies):
        occurrences = session.get("occurrences", [])
        for i, occurrence in enumerate(occurrences):
            occurrences[i]["endTime"] = self._parse_timestr(occurrence["endTime"])
            occurrences[i]["startTime"] = self._parse_timestr(occurrence["startTime"])
        session["occurrences"] = occurrences
        self.course = course
        self.session = session
        self._cookies = cookies

    def _parse_timestr(self, timestr):
        return datetime.fromisoformat(timestr.replace("Z", "+00:00"))

    def next_occurrence(self):
        utcnow = datetime.now(timezone.utc)
        for occurrence in self.session["occurrences"]:
            if not occurrence["endTime"] < utcnow:
                return occurrence
        return None

    def join(self):
        url = ENDPOINTS["launch_session"].format(course_id=self.course["id"], session_id=self.session["id"])
        xsrf_token = self._extract_xsrf_token_from_cookie(self._cookies["BbRouter"])
        headers = {"X-Blackboard-XSRF": xsrf_token}
        response = requests.post(url, headers=headers, cookies=self._cookies)
        return response.json()

    def _extract_xsrf_token_from_cookie(self, cookie):
        to_search = "xsrf:"
        position = cookie.find(to_search) + len(to_search)
        xsrf_token = cookie[position:]
        return xsrf_token

    def __le__(self, session):
        return self.session.next_occurrence() < session.session.next_occurrence()

