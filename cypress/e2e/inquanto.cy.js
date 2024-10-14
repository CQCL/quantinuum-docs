const checkThatNavBarExists = () => {
  cy.get('nav').contains(/inquanto/i).parent().parent().within(() => {
    cy.contains(/inquanto/i)
  })
}

describe('E2E Tests', () => {
  it('can view / (landing page)', () => {
    cy.visit('http://localhost:3000/inquanto/')
    checkThatNavBarExists()
    cy.contains(/quantum chemistry on quantum computers/i)
    cy.contains(/access inquanto/i)
    cy.contains(/chemical specification/i)
    cy.contains(/program construction/i)
    cy.contains(/execution and analysis/i)
  })

  it("examples is accessed from Navbar -> InQuanto", () => {  
    cy.visit('http://localhost:3000/inquanto/')
    cy.contains('button', 'InQuanto').should('be.visible')
    cy.contains('button', 'InQuanto', { timeout: 15000 }).click();
    cy.contains(/toolkit for complex molecular and materials simulations/i).should("be.visible")
    cy.contains(/introduction/i).should("be.visible")
    cy.contains(/user guide/i).should("be.visible")
    cy.contains(/tutorials/i).should("be.visible")
    cy.contains(/examples/i).should("be.visible").click();
    cy.contains(/overview of examples/i)
  })

  it('can view user guide', () => {
    cy.visit('http://localhost:3000/inquanto/manual/howto.html')
    checkThatNavBarExists()
    cy.contains(/How to use InQuanto/i)
  })

  it('can view introduction', () => {
    cy.visit('http://localhost:3000/inquanto/introduction/overview.html')
    checkThatNavBarExists()
    cy.contains(/what is inquanto?/i)
    cy.contains(/why use inquanto?/i)
  })

  it('inspect getting tutorials page', () => {
    cy.visit('http://localhost:3000/inquanto/tutorials/tutorial_overview.html')
    checkThatNavBarExists()
    cy.contains(/tutorials/i)
    cy.contains(/core tutorials/i)
    cy.contains(/these tutorial notebooks contain more guided examples of using the functionality in inquanto and its extensions to simulate quantum chemistry using quantum computers./i)
  })

  it('inspect examples page', () => {
    cy.visit('http://localhost:3000/inquanto/tutorials/examples_overview.html')
    checkThatNavBarExists()
    cy.contains(/overview of examples/i)
    cy.contains(/in addition to the detailed tutorials, inquanto contains several example scripts showing how various functionality is used. /i)
    cy.contains(/qse/i)
  })

  if("inspect api reference", () => {
    cy.visit('http://localhost:3000/inquanto/api/inquanto_api_intro.html')
    checkThatNavBarExists()
    cy.contains('inquanto api reference')
  })

 it.skip('can link to root docs page from inquanto guides page', () => {
    cy.visit('http://localhost:3000/inquanto/guides.html')
   cy.findByLabelText(/quantinuum documentation/i).click()
  cy.origin('https://docs.quantinuum.com', () => {
  cy.contains(/technical documentation/i)
 })
})
})
