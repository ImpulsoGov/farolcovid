import streamlit as st
import amplitude
import utils


def main(session_state):
    user_analytics = amplitude.gen_user(utils.get_server_session())
    opening_response = user_analytics.safe_log_event(
        "opened saude_em_ordem_description", session_state, is_new_page=True
    )
    st.header("""Farol Covid""")
    st.subheader("""1. Introdução""")
    st.write(
        """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent dignissim lacus nec lacus iaculis, id vehicula diam suscipit. Etiam consequat nisl lectus, id vulputate risus dapibus sed. Nulla ut lobortis tellus. Sed gravida consequat lectus, vitae mattis dolor tempus sit amet. Nullam venenatis augue ante, id lobortis ligula pretium in. Donec vulputate imperdiet porttitor. Ut varius nunc at ullamcorper fermentum. Nullam laoreet suscipit pulvinar. Vestibulum iaculis dictum nulla, ut pellentesque eros rutrum sit amet. Duis egestas quis neque vitae molestie. Nam nec est non nisl scelerisque consectetur nec vel nibh. Mauris non hendrerit purus. Suspendisse efficitur urna non lacus placerat facilisis. Curabitur eros libero, pretium ut dolor eget, dictum fringilla ante. Etiam sollicitudin tellus nulla, nec faucibus ante placerat ac.

    Sed molestie feugiat ipsum at viverra. Fusce ac ipsum nisl. Donec pellentesque ipsum non imperdiet imperdiet. Fusce porta mi in mi blandit, quis hendrerit magna tristique. Curabitur egestas dolor quam, malesuada condimentum lorem euismod nec. Aenean mattis sapien suscipit, sodales risus in, auctor massa. In non tellus at enim lobortis ultrices.
    """
    )
    st.subheader("2. Dados")
    st.write(
        """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent dignissim lacus nec lacus iaculis, id vehicula diam suscipit. Etiam consequat nisl lectus, id vulputate risus dapibus sed. Nulla ut lobortis tellus. Sed gravida consequat lectus, vitae mattis dolor tempus sit amet. Nullam venenatis augue ante, id lobortis ligula pretium in. Donec vulputate imperdiet porttitor. Ut varius nunc at ullamcorper fermentum. Nullam laoreet suscipit pulvinar. Vestibulum iaculis dictum nulla, ut pellentesque eros rutrum sit amet. Duis egestas quis neque vitae molestie. Nam nec est non nisl scelerisque consectetur nec vel nibh. Mauris non hendrerit purus. Suspendisse efficitur urna non lacus placerat facilisis. Curabitur eros libero, pretium ut dolor eget, dictum fringilla ante. Etiam sollicitudin tellus nulla, nec faucibus ante placerat ac.

    Sed molestie feugiat ipsum at viverra. Fusce ac ipsum nisl. Donec pellentesque ipsum non imperdiet imperdiet. Fusce porta mi in mi blandit, quis hendrerit magna tristique. Curabitur egestas dolor quam, malesuada condimentum lorem euismod nec. Aenean mattis sapien suscipit, sodales risus in, auctor massa. In non tellus at enim lobortis ultrices.
    """
    )
    st.subheader("3. Metodologia")
    st.write(
        """
    #### a. índice de x

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent dignissim lacus nec lacus iaculis, id vehicula diam suscipit. Etiam consequat nisl lectus, id vulputate risus dapibus sed. Nulla ut lobortis tellus. Sed gravida consequat lectus, vitae mattis dolor tempus sit amet. Nullam venenatis augue ante, id lobortis ligula pretium in. Donec vulputate imperdiet porttitor. Ut varius nunc at ullamcorper fermentum. Nullam laoreet suscipit pulvinar. Vestibulum iaculis dictum nulla, ut pellentesque eros rutrum sit amet. Duis egestas quis neque vitae molestie. Nam nec est non nisl scelerisque consectetur nec vel nibh. Mauris non hendrerit purus. Suspendisse efficitur urna non lacus placerat facilisis. Curabitur eros libero, pretium ut dolor eget, dictum fringilla ante. Etiam sollicitudin tellus nulla, nec faucibus ante placerat ac.

    Sed molestie feugiat ipsum at viverra. Fusce ac ipsum nisl. Donec pellentesque ipsum non imperdiet imperdiet. Fusce porta mi in mi blandit, quis hendrerit magna tristique. Curabitur egestas dolor quam, malesuada condimentum lorem euismod nec. Aenean mattis sapien suscipit, sodales risus in, auctor massa. In non tellus at enim lobortis ultrices.
    #### b. índice de y
    
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent dignissim lacus nec lacus iaculis, id vehicula diam suscipit. Etiam consequat nisl lectus, id vulputate risus dapibus sed. Nulla ut lobortis tellus. Sed gravida consequat lectus, vitae mattis dolor tempus sit amet. Nullam venenatis augue ante, id lobortis ligula pretium in. Donec vulputate imperdiet porttitor. Ut varius nunc at ullamcorper fermentum. Nullam laoreet suscipit pulvinar. Vestibulum iaculis dictum nulla, ut pellentesque eros rutrum sit amet. Duis egestas quis neque vitae molestie. Nam nec est non nisl scelerisque consectetur nec vel nibh. Mauris non hendrerit purus. Suspendisse efficitur urna non lacus placerat facilisis. Curabitur eros libero, pretium ut dolor eget, dictum fringilla ante. Etiam sollicitudin tellus nulla, nec faucibus ante placerat ac.

    Sed molestie feugiat ipsum at viverra. Fusce ac ipsum nisl. Donec pellentesque ipsum non imperdiet imperdiet. Fusce porta mi in mi blandit, quis hendrerit magna tristique. Curabitur egestas dolor quam, malesuada condimentum lorem euismod nec. Aenean mattis sapien suscipit, sodales risus in, auctor massa. In non tellus at enim lobortis ultrices.
    """
    )

    #gen_table()
    st.write(
        """
    ### c. Ordenamento setorial

    Pellentesque non finibus massa. Cras quis metus ut nunc porta lacinia. Nullam ut dolor sed felis fermentum fermentum. Nunc nec nisi scelerisque, pellentesque nibh ut, scelerisque turpis. Integer ultricies, mauris id porttitor consectetur, dui magna efficitur velit, at aliquam neque justo eu nisi. Suspendisse non vulputate lacus. Quisque a consectetur metus. Nunc sagittis quam quis arcu porttitor, scelerisque blandit tortor tincidunt. Morbi vehicula dui neque, in varius justo ornare vitae. Vivamus fringilla elit sed est fringilla feugiat.
    """
    )
    st.subheader("Referências")
    st.write(
        """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent dignissim lacus nec lacus iaculis, id vehicula diam suscipit. Etiam consequat nisl lectus, id vulputate risus dapibus sed. Nulla ut lobortis tellus. Sed gravida consequat lectus, vitae mattis dolor tempus sit amet. Nullam venenatis augue ante, id lobortis ligula pretium in. Donec vulputate imperdiet porttitor. Ut varius nunc at ullamcorper fermentum. Nullam laoreet suscipit pulvinar. Vestibulum iaculis dictum nulla, ut pellentesque eros rutrum sit amet. Duis egestas quis neque vitae molestie. Nam nec est non nisl scelerisque consectetur nec vel nibh. Mauris non hendrerit purus. Suspendisse efficitur urna non lacus placerat facilisis. Curabitur eros libero, pretium ut dolor eget, dictum fringilla ante. Etiam sollicitudin tellus nulla, nec faucibus ante placerat ac.

        Sed molestie feugiat ipsum at viverra. Fusce ac ipsum nisl. Donec pellentesque ipsum non imperdiet imperdiet. Fusce porta mi in mi blandit, quis hendrerit magna tristique. Curabitur egestas dolor quam, malesuada condimentum lorem euismod nec. Aenean mattis sapien suscipit, sodales risus in, auctor massa. In non tellus at enim lobortis ultrices.
       """
    )


def gen_table():
    st.write(
        """
        """,
        unsafe_allow_html=True,
    )

