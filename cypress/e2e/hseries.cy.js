import { checkThatNavBarExists } from './utils';

describe('E2E Tests', () => {
    it('view landing page', () => {
        cy.visit('/h-series/')
        checkThatNavBarExists()
        cy.contains(/the world's highest-performing quantum hardware/i)
        cy.contains(/access h-series/i)
        cy.contains(/hardware specifications/i)
        cy.contains(/quantum volume data/i)
        cy.contains(/hardware user guide/i)
        cy.contains(/emulator user guide/i)
        cy.contains(/getting started/i)
        // cy.contains(/support/i)
    })
    
    it("support is accessed from Navbar -> H-Series", {
        retries: {
          // Nav dropdown is flaky at the moment.
          runMode: 5,
          openMode: 5,
        }
      },() => {  
        cy.visit('/h-series/')
        checkThatNavBarExists()
        cy.contains('button', 'H-Series').should('be.visible').click();
        cy.contains(/quantinuum's qccd ion-trap hardware/i).should("be.visible")
        cy.contains(/guides/i).should("be.visible")
        cy.contains(/getting started/i).should("be.visible")
        cy.contains(/knowledge articles/i).should("be.visible")
        cy.contains(/support/i).should("be.visible").click()
        cy.contains(/support/i)
        cy.contains(/product change notifications/i)
        cy.contains(/troubleshooting/i)
        cy.contains(/faqs/i)
        cy.contains(/how to cite h-series/i)
    })
    
    it('Inspect Hardware User Guide', () => {
        cy.visit('/h-series/user_guide/hardware_user_guide/access')
        cy.contains(/h-series systems/i)
        cy.contains(/quantum computers/i)
    })

    it('Inspect Emulator User Guide', () => {
        cy.visit('/h-series/user_guide/emulator_user_guide/introduction')
        cy.contains(/h-series emulators/i)
        cy.contains(/use cases/i)
    })

    it('ka 1', () => {
        cy.visit('/h-series/trainings/knowledge_articles/Quantinuum_toric_code')
        cy.contains(/topological order/i)
        cy.contains(/toric code/i)
        cy.contains(/feed-forward/i)
    })

    it('ka 2', () => {
        cy.visit('/h-series/trainings/knowledge_articles/Quantinuum_chemistry_chemically_aware_ucc')
        cy.contains(/quantum chemistry calculations with arbitrary angle 2-qubit gates/i)
        cy.contains(/hamiltonian specification/i)
    })

    it.skip('can link to root docs page from h-series guides page', () => {
        cy.visit('/h-series/guides.html')
        cy.findByLabelText(/quantinuum documentation/i).click()
        cy.origin('https://docs.quantinuum.com', () => {
        cy.contains(/technical documentation/i)
    })})
})