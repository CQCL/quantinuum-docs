const checkThatNavBarExists = () => {
  cy.get('nav').contains(/nexus/i).parent().parent().within(() => {
    cy.contains(/nexus/i)
  })
}

describe('E2E Tests', () => {
  it('can view / (landing page)', () => {
    cy.visit('/nexus/')
    checkThatNavBarExists()
    cy.contains(/The Full Stack Quantum Computing Platform/i)
    cy.contains(/pip install qnexus/i)
    cy.contains(/Guides/i)
    cy.contains(/Getting Started/i)
    cy.contains(/Advanced Users/i)

  })

  it("support is accessed from Navbar -> Nexus", {
    retries: {
      // Nav dropdown is flaky at the moment.
      runMode: 5,
      openMode: 5,
    }
  },() => {  
    cy.visit('/nexus/')
    cy.contains('button', 'Nexus').should("be.visible")
    cy.contains('button', 'Nexus', { timeout: 15000 }).click();
    cy.contains(/Cloud platform connecting users with hardware/i).should("be.visible")
    cy.contains(/Guides/i).should("be.visible")
    cy.contains(/Trainings/i).should("be.visible")
    cy.contains(/Api Reference/i).should("be.visible")
    cy.contains(/Support/i).should("be.visible").click();    
    cy.contains(/Support/i)
    cy.contains(/This section provides information on how to get support for the Nexus platform./i)
  })

  it('can view user guide', () => {
    cy.visit('/nexus/user_guide/sign_up.html')
    checkThatNavBarExists()
    cy.contains(/Signing Up/i)
  })

  it('can view admin guide', () => {
    cy.visit('/nexus/admin_guide/admin_guide.html')
    checkThatNavBarExists()
    cy.contains(/admin guide/i)
    cy.contains(/This section contains guides on navigating the Quantinuum Nexus web UI to perform administrator actions./i)
  })

  it('inspect getting started page', () => {
    cy.visit('/nexus/trainings/notebooks/getting_started.html')
    checkThatNavBarExists()
    cy.contains(/Getting Started with qnexus/i)
    cy.contains(/pip install qnexus/i)

  })

 it.skip('can link to root docs page from nexus guides page', () => {
    cy.visit('/nexus/guides.html')
   cy.findByLabelText(/quantinuum documentation/i).click()
  cy.origin('https://docs.quantinuum.com', () => {
  cy.contains(/technical documentation/i)
 })
})
})
