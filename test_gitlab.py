
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import pytest
import pdb

# tests using selenium-python plugin to test the UI of Gitlab
# these tests are run from a Docker instance of GitLab, running on the local host

# setup password method


def setup_method(selenium, method):
    setup_password(selenium)

# use headless chrome for testing


@pytest.fixture
def chrome_options(chrome_options, pytestconfig):
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    return chrome_options


# tests using selenium-python plugin to test the UI of Gitlab
# these tests are run from a Docker instance of GitLab, running on the local host

# from command line, run: pytest -v --driver chrome test_gitlab.py to run all the tests
# from command line, run: pytest -v --driver chrome test_gitlab.py -k test_page_title to run just the first test. Replace 'test_page_title' with the name of whichever individual test to be run.
# pass selenium fixture (from python-selenium plugin) to each test


# test to see if Gitlab is in the title of the local host page
def test_page_title(selenium):
    selenium.implicitly_wait(15)
    selenium.maximize_window()
    selenium.get('http://localhost')
    assert 'GitLab' in selenium.title

# test that sets the password as "p455w0rd"


def setup_password(selenium):
    test_page_title(selenium)
    if selenium.current_url.find("reset_password_token") > -1:
        selenium.find_element_by_id('user_password').send_keys('p455w0rd')
        selenium.find_element_by_id(
            'user_password_confirmation').send_keys('p455w0rd')
        selenium.find_element_by_name('commit').click()

# test of the login button on the Gitlab home page


def test_login_button(selenium):
    setup_password(selenium)
    elem = selenium.find_element_by_link_text("Sign in")
    elem.click()
    assert "Username or email" in selenium.page_source

# test the login functionality using  'root' as username and 'p455w0rd' as the password


def test_login(selenium):
    test_login_button(selenium)
    selenium.maximize_window()
    selenium.find_element_by_id('user_login').send_keys('root')
    selenium.find_element_by_id('user_password').send_keys('p455w0rd')
    selenium.find_element_by_name('commit').click()


# test the search bar to find repositories that have 'Python' in their title
def test_search_repos(selenium):
    test_login(selenium)
    elem = selenium.find_element_by_id('search')
    assert elem is not None
    elem.send_keys("Python")
    elem.send_keys(Keys.RETURN)
    assert 'Python' in selenium.title

# test the create new repository button


def test_new_project_button1(selenium):
    test_login(selenium)
    selenium.refresh()
    selenium.find_element_by_class_name('blank-state-link').click()
    assert "New project" in selenium.page_source


# test to create a new project
def test_create_new_project(selenium):
    test_new_project_button1(selenium)
    selenium.find_element_by_id('project_name').send_keys('testing project')
    selenium.find_element_by_id('project_path').send_keys('my-project')
    selenium.find_element_by_id(
        'project_description').send_keys('details awaited')
    selenium.find_element_by_id('project_visibility_level_20').click()
    selenium.find_element_by_name('commit').click()
    assert "testing project" in selenium.page_source

# test to create a new file


def test_create_new_file1(selenium):
    test_login(selenium)
    selenium.get("http://localhost/root/testing-projectmy-project")
    selenium.find_element_by_link_text('New file').click()
    selenium.find_element_by_class_name('dropdown-toggle-text').click()
    selenium.find_element_by_link_text('.gitignore').click()
    selenium.find_element_by_id('file_name').send_keys('abcd')
    selenium.find_element_by_class_name(
        'ace_text-input').send_keys('random text')
    selenium.find_element_by_name('commit_message').send_keys('yay commit')
    selenium.find_element_by_id('file_name').send_keys(Keys.RETURN)
    assert "abcd" in selenium.page_source


def test_find_file(selenium):
    test_login(selenium)
    selenium.find_element_by_partial_link_text('testing').click()
    selenium.find_element_by_link_text('Find file').click()
    selenium.find_element_by_id('file_find').send_keys('abcd')
    time.sleep(3)
    selenium.find_element_by_id("file_find").send_keys(Keys.RETURN)
    assert "abcd" in selenium.page_source

# test to edit/update an existing file in the repository


def test_edit_file(selenium):
    test_find_file(selenium)
    selenium.find_element_by_link_text('Edit').click()
    selenium.find_element_by_class_name('ace_content').click()
    selenium.find_element_by_class_name('ace_text-input').send_keys('more')
    selenium.find_element_by_class_name('commit-btn').click()
    assert "more" in selenium.page_source

# test to delete an existing file


def test_delete_file(selenium):
    test_find_file(selenium)
    selenium.find_element_by_class_name('btn-remove').click()
    selenium.find_element_by_class_name('btn-remove-file').click()

# test to delete an existing repository


def test_remove_repository(selenium):
    test_login(selenium)
    selenium.get("http://localhost/root/testing-projectmy-project/edit")
    selenium.find_element_by_xpath(
        "//h4[text()='Advanced']/following-sibling::button[text()='Expand']").click()
    selenium.find_element_by_xpath("//input[@value='Remove project']").click()
    selenium.find_element_by_id("confirm_name_input").click()
    selenium.find_element_by_id("confirm_name_input").clear()
    selenium.find_element_by_id("confirm_name_input").send_keys(
        "testing-projectmy-project")
    selenium.find_element_by_class_name("js-confirm-danger-submit").click()
    selenium.refresh()
    selenium.refresh()
    assert selenium.current_url == "http://localhost/dashboard/projects"

# test to logout of Gitlab


def test_logout(selenium):
    test_login(selenium)
    selenium.find_element_by_class_name("qa-js-lazy-loaded").click()
    selenium.find_element_by_class_name("sign-out-link").click()
    assert "Sign in" in selenium.page_source
