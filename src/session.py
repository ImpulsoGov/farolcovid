# Session State functions from external Gists
# - SessionState.py: https://gist.github.com/tvst/036da038ab3e999a64497f42de966a92
# - st_rerun.py: https://gist.github.com/tvst/ef477845ac86962fa4c92ec6a72bb5bd

# NEW TRY: https://gist.github.com/tvst/0899a5cdc9f0467f7622750896e6bd7f

import streamlit.ReportThread as ReportThread
from streamlit.server.Server import Server
from streamlit.ScriptRequestQueue import RerunData
from streamlit.ScriptRunner import RerunException

import inspect
import os
import threading
import collections


def rerun():
    print("Rerruning")
    """Rerun a Streamlit app from the top!"""
    widget_states = _get_widget_states()
    raise RerunException(RerunData(widget_states))


def get_user_id():
    ctx = ReportThread.get_report_ctx()
    session_infos = Server.get_current()._session_info_by_id.values()
    # print(dir(session_infos[0]))
    for session_info in session_infos:
        # print("Session info session dir:")
        # print(dir(session_info.session))
        if session_info.session.enqueue == ctx.enqueue:
            user_id = session_info.session.id
            # print("Current: " + str(session_info.session.id))
        else:
            # print(session_info.session.id)
            pass
    return user_id


def _get_widget_states():
    ctx = ReportThread.get_report_ctx()

    session = None
    session_infos = Server.get_current()._session_info_by_id.values()

    for session_info in session_infos:
        if session_info.session.enqueue == ctx.enqueue:
            session = session_info.session

    if session is None:
        raise RuntimeError(
            "Oh noes. Couldn't get your Streamlit Session object"
            "Are you doing something fancy with threads?"
        )

    return session._widget_states


class SessionState(object):
    # FROM NEW TRY
    def __new__(cls, key=None, **kwargs):

        states_dict, key_counts = _get_session_state()

        if key in states_dict:
            return states_dict[key]
        else:
            state = super(SessionState, cls).__new__(cls)
            states_dict[key] = state

            return state

    def __init__(self, **kwargs):
        """A new SessionState object.
        Parameters
        ----------
        **kwargs : any
            Default values for the session state.
        Example
        -------
        >>> session_state = SessionState(user_name='', favorite_color='black')
        >>> session_state.user_name = 'Mary'
        ''
        >>> session_state.favorite_color
        'black'
        """
        for key, val in kwargs.items():
            setattr(self, key, val)

    def get(**kwargs):
        """Gets a SessionState object for the current session.
        Creates a new object if necessary.
        Parameters
        ----------
        **kwargs : any
            Default values you want to add to the session state, if we're creating a
            new one.
        Example
        -------
        >>> session_state = get(user_name='', favorite_color='black')
        >>> session_state.user_name
        ''
        >>> session_state.user_name = 'Mary'
        >>> session_state.favorite_color
        'black'
        Since you set user_name above, next time your script runs this will be the
        result:
        >>> session_state = get(user_name='', favorite_color='black')
        >>> session_state.user_name
        'Mary'
        """
        # Hack to get the session object from Streamlit.

        ctx = ReportThread.get_report_ctx()

        this_session = None

        current_server = Server.get_current()
        if hasattr(current_server, "_session_infos"):
            # Streamlit < 0.56
            session_infos = Server.get_current()._session_infos.values()
        else:
            session_infos = Server.get_current()._session_info_by_id.values()

        for session_info in session_infos:
            s = session_info.session
            if (
                # Streamlit < 0.54.0
                (hasattr(s, "_main_dg") and s._main_dg == ctx.main_dg)
                or
                # Streamlit >= 0.54.0
                (not hasattr(s, "_main_dg") and s.enqueue == ctx.enqueue)
            ):
                this_session = s

        if this_session is None:
            raise RuntimeError(
                "Oh noes. Couldn't get your Streamlit Session object"
                "Are you doing something fancy with threads?"
            )

        # Got the session object! Now let's attach some state into it.

        if not hasattr(this_session, "_custom_session_state"):
            this_session._custom_session_state = SessionState(**kwargs)

        return this_session._custom_session_state


# FROM NEW TRY
def _get_session_state():
    session = _get_session_object()

    curr_thread = threading.current_thread()

    if not hasattr(session, "_session_state"):
        session._session_state = {}

    if not hasattr(curr_thread, "_key_counts"):
        # Put this in the thread because it gets cleared on every run.
        curr_thread._key_counts = collections.defaultdict(int)

    return session._session_state, curr_thread._key_counts


def _get_session_raw():
    # Hack to get the session object from Streamlit.

    ctx = ReportThread.get_report_ctx()

    this_session = None

    current_server = Server.get_current()
    if hasattr(current_server, "_session_infos"):
        # Streamlit < 0.56
        session_infos = Server.get_current()._session_infos.values()
    else:
        session_infos = Server.get_current()._session_info_by_id.values()

    for session_info in session_infos:
        s = session_info
        if (
            # Streamlit < 0.54.0
            (hasattr(s, "_main_dg") and s.session._main_dg == ctx.main_dg)
            or
            # Streamlit >= 0.54.0
            (not hasattr(s, "_main_dg") and s.session.enqueue == ctx.enqueue)
        ):
            this_session = s

    if this_session is None:
        raise RuntimeError(
            "Oh noes. Couldn't get your Streamlit Session object"
            "Are you doing something fancy with threads?"
        )
    return this_session


def _get_session_object():
    return _get_session_raw().session
